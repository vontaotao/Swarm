"""
# 1. 功能
去中心化匹配算法模块。不使用中央 matcher，无人机通过通信网络
交换声明消息，自主协商完成到目标快照的补位分配。

# 2. 输入
- snapshot: 布尔网格 (np.ndarray)
- drones: Drone 列表
- comm: CommNetwork 实例
- max_rounds: 每时间步最多协商轮数

# 3. 输出
- 直接修改各无人机的目标位置（内部调用 move_toward）

# 4. 核心执行流程
每轮（sub-step）：
  1. 收集所有无人机当前位置，更新通信网络
  2. 每架无人机检查自己是否在目标像素上 → 是则 CLAIM
  3. 从通信消息中收集所有已声明的空缺
  4. 未分配无人机找最近未被声明的空缺 → 广播 CLAIM
  5. 冲突解决：同一空缺多人声明 → 距离最近者胜，失败者下轮重试
  6. 无人机向各自声明目标 move_toward
  7. 收敛判断：所有无人机已到达目标 或 无新声明产生

# 5. 依赖
- numpy
- src.drone, src.comm, src.matcher（复用 _vacancies_from_snapshot）
"""

import numpy as np
from src.drone import Drone
from src.comm import CommNetwork
from src.matcher import _vacancies_from_snapshot, _pixel_at, _sq_dist

_MAX_ROUNDS = 100


def distributed_match(
    snapshot: np.ndarray,
    drones: list[Drone],
    comm: CommNetwork,
    max_rounds: int = _MAX_ROUNDS,
) -> None:
    """执行一个时间步的去中心化匹配，无人机通过通信协商补位。

    直接修改 drones 的位置（通过 move_toward）。

    Args:
        snapshot: 目标快照
        drones: 无人机列表
        comm: 已初始化的通信网络
        max_rounds: 最大协商轮数
    """
    n = len(drones)
    if n == 0:
        return

    all_vacancies = _vacancies_from_snapshot(snapshot)
    if not all_vacancies:
        return

    # 每架无人机的当前声明目标
    claims: dict[int, tuple[int, ...] | None] = {}  # drone_id -> pixel or None

    for _round in range(max_rounds):
        # 更新通信网络中的位置
        pos_map = {d.id: d.position for d in drones}
        comm.update_positions(pos_map)
        comm.clear()

        # --- 阶段 1: 在位检测，已占稳的广播 CLAIM ---
        for d in drones:
            if d.id in claims and claims[d.id] is not None:
                # 已有声明，检查是否到达
                target = claims[d.id]
                if _pixel_at(d.position) == target:
                    comm.broadcast(d.id, "CLAIM", target=target)
                    continue
                # 还没到达，继续移动
            else:
                # 检查是否已在目标像素上
                pixel = _pixel_at(d.position)
                if pixel in all_vacancies:
                    claims[d.id] = pixel
                    comm.broadcast(d.id, "CLAIM", target=pixel)

        # --- 阶段 2: 收集已声明的空缺 ---
        claimed_pixels: set[tuple[int, ...]] = set()
        for d in drones:
            for msg in comm.receive(d.id):
                if msg["type"] == "CLAIM" and "target" in msg:
                    claimed_pixels.add(msg["target"])

        # 加上自己刚声明的
        for d in drones:
            if d.id in claims and claims[d.id] is not None:
                claimed_pixels.add(claims[d.id])

        # --- 阶段 3: 未分配无人机找最近空缺并广播声明 ---
        round_new_claims: dict[int, tuple[int, ...]] = {}  # drone_id -> pixel (本轮新声明)
        for d in drones:
            if d.id in claims and claims[d.id] is not None:
                continue  # 已有声明

            unclaimed = [v for v in all_vacancies if v not in claimed_pixels]
            if not unclaimed:
                break

            # 找最近未声明空缺
            best_vac: tuple[int, ...] | None = None
            best_dist = float("inf")
            for vac in unclaimed:
                dist = _sq_dist(d.position, vac)
                if dist < best_dist:
                    best_dist = dist
                    best_vac = vac

            if best_vac is not None:
                round_new_claims[d.id] = best_vac
                claimed_pixels.add(best_vac)

        # 广播新声明
        for drone_id, target in round_new_claims.items():
            comm.broadcast(drone_id, "CLAIM", target=target)

        # --- 阶段 4: 冲突检测 ---
        # 收集本轮所有声明（含已有和新声明）
        all_claims_this_round: dict[int, tuple[int, ...]] = {}
        # 已有声明保持不变
        for d in drones:
            if d.id in claims and claims[d.id] is not None:
                all_claims_this_round[d.id] = claims[d.id]

        # 新声明加入
        for drone_id, target in round_new_claims.items():
            all_claims_this_round[drone_id] = target
            claims[drone_id] = target

        # 检测冲突：同一空缺被多人声明
        pixel_claimers: dict[tuple[int, ...], list[int]] = {}
        for drone_id, target in all_claims_this_round.items():
            pixel_claimers.setdefault(target, []).append(drone_id)

        for target, drone_ids in pixel_claimers.items():
            if len(drone_ids) > 1:
                # 保留距离最近的
                best_id = min(drone_ids, key=lambda i: _sq_dist(
                    _drone_by_id(drones, i).position, target
                ))
                for i in drone_ids:
                    if i != best_id:
                        # 失败者清除声明
                        claims[i] = None

        # --- 阶段 5: 移动 ---
        any_moving = False
        for d in drones:
            if d.id in claims and claims[d.id] is not None:
                target = claims[d.id]
                arrived = d.move_toward(float(target[0]), float(target[1]),
                                         float(target[2]) if len(target) > 2 else 0.0)
                if not arrived:
                    any_moving = True
            else:
                # 无声明 → 本轮不动
                pass

        # --- 阶段 6: 收敛判断 ---
        if not any_moving:
            # 检查是否所有无人机都在目标像素上
            all_arrived = True
            for d in drones:
                if _pixel_at(d.position) not in all_vacancies:
                    all_arrived = False
                    break
            if all_arrived:
                break


def _drone_by_id(drones: list[Drone], drone_id: int) -> Drone:
    """根据 ID 查找无人机。"""
    for d in drones:
        if d.id == drone_id:
            return d
    raise KeyError(f"Drone {drone_id} not found")
