"""
# 1. 功能
主仿真循环模块。串联网格、无人机、匹配算法，驱动时间步推进，
记录每个时刻的无人机位置轨迹。

支持三种维度模式：
- 集中式（mode="centralized"）：使用 matcher.match() 全局匹配
- 去中心化（mode="distributed"）：无人机通过通信协商完成补位

# 2. 输入
- snapshots: 快照列表
- n_drones: 无人机数量
- mode: "centralized" 或 "distributed"
- comm_radius: 通信半径（distributed 模式）

# 3. 输出
- trajectory: list[list[(x, y, z)]]

# 4. 核心执行流程
1. 初始化无人机群（随机散布）
2. 循环每时间步：
   a. centralized: match + move_toward 内层循环
   b. distributed: distributed_match 协商循环
   c. 记录轨迹

# 5. 依赖
- numpy, random
- src.drone, src.matcher, src.comm, src.distributed_matcher
"""

import random
import numpy as np

from src.drone import Drone
from src.matcher import match
from src.comm import CommNetwork
from src.distributed_matcher import distributed_match

_MAX_SUB_STEPS = 200


def _init_drones(
    n: int,
    shape: tuple[int, ...],
    seed: int = 0,
    max_speed: float = float("inf"),
) -> list[Drone]:
    """在网格内随机散布 n 架无人机。

    Args:
        shape: 网格形状，(height, width) 或 (depth, height, width)
    """
    rng = random.Random(seed)
    drones = []
    if len(shape) == 2:
        height, width = shape
        for i in range(n):
            drones.append(Drone(i, rng.uniform(0, width - 1),
                                 rng.uniform(0, height - 1),
                                 max_speed=max_speed))
    else:
        depth, height, width = shape
        for i in range(n):
            drones.append(Drone(i, rng.uniform(0, width - 1),
                                 rng.uniform(0, height - 1),
                                 rng.uniform(0, depth - 1),
                                 max_speed=max_speed))
    return drones


def run(
    snapshots: list[np.ndarray],
    n_drones: int,
    seed: int = 0,
    verbose: bool = True,
    max_speed: float = float("inf"),
    mode: str = "centralized",
    comm_radius: float = float("inf"),
) -> list[list[tuple[float, float, float]]]:
    """运行多时间步仿真。

    Args:
        snapshots: 快照序列
        n_drones: 无人机数量
        seed: 随机种子
        verbose: 是否打印
        max_speed: 最大移动速度
        mode: "centralized" 或 "distributed"
        comm_radius: 通信半径（distributed 模式使用）

    Returns:
        trajectory[t][i] = 第 t 步第 i 架无人机的 (x, y, z)
    """
    if not snapshots:
        return []

    shape = snapshots[0].shape
    drones = _init_drones(n_drones, shape, seed, max_speed=max_speed)

    if mode == "distributed":
        comm = CommNetwork(comm_radius=comm_radius)

    trajectory: list[list[tuple[float, float, float]]] = []

    for t, snapshot in enumerate(snapshots):
        if mode == "centralized":
            # --- 集中式：matcher + 内层收敛 ---
            for _sub_step in range(_MAX_SUB_STEPS):
                positions = [d.position for d in drones]
                targets = match(snapshot, positions)

                any_moving = False
                for d, target in zip(drones, targets):
                    tx, ty = target[0], target[1]
                    tz = target[2] if len(target) > 2 else 0.0
                    arrived = d.move_toward(tx, ty, tz)
                    if not arrived:
                        any_moving = True

                if not any_moving:
                    break
        else:
            # --- 去中心化：通信协商 ---
            distributed_match(snapshot, drones, comm)

        step_positions = [d.position for d in drones]
        trajectory.append(step_positions)

        if verbose:
            _print_step(t, snapshot, step_positions, drones)

    return trajectory


def run_single_step(
    snapshot: np.ndarray,
    drone_positions: list[tuple[float, ...]],
) -> list[tuple[float, ...]]:
    """单步仿真：给定快照和当前位置，返回分配后的新位置。"""
    return match(snapshot, drone_positions)


def _print_step(
    t: int,
    snapshot: np.ndarray,
    positions: list[tuple[float, ...]],
    drones: list[Drone],
) -> None:
    """打印单步状态摘要。"""
    n_targets = int(np.sum(snapshot))
    n_drones = len(positions)
    in_position = 0
    for pos in positions:
        pixel = tuple(int(round(c)) for c in pos)
        # 转换为 (row, col) 或 (depth, row, col) 索引
        idx = tuple(reversed(pixel))
        all_ok = all(0 <= idx[i] < snapshot.shape[i] for i in range(len(idx)))
        if all_ok and snapshot[idx]:
            in_position += 1
    print(f"--- 时间步 t={t} ---")
    print(f"  目标像素数: {n_targets},  无人机数: {n_drones},  已就位: {in_position}")
    if n_drones <= 10:
        for d in drones:
            print(f"  {d}")
