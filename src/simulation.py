"""
# 1. 功能
主仿真循环模块。串联网格、无人机、匹配算法，驱动时间步推进，
记录每个时刻的无人机位置轨迹。

支持两种模式：
- 瞬时模式（max_speed=inf）：每个时间步一次匹配 + 瞬时传送
- 速度约束模式（max_speed 有限）：每个时间步内迭代匹配 + 渐进移动直到收敛

# 2. 输入
- 仿真参数：无人机数量、网格尺寸、时间步数、快照序列、max_speed

# 3. 输出
- trajectory: list[list[(x, y)]]，每个时间步的全体无人机位置
- 命令行打印每步状态

# 4. 核心执行流程
1. 初始化无人机群（随机散布在网格内）
2. 循环 t = 0 → max_steps:
   a. 获取当前快照 S(t)
   b. 内层收敛循环：
      - 调用 matcher.match() 得到目标位置
      - 无人机 move_toward() 逐步靠近目标
      - 重复直到全部就位或无空缺
   c. 记录轨迹
   d. 命令行打印状态摘要
3. 返回完整轨迹

# 5. 依赖
- numpy, random
- src.grid, src.drone, src.matcher
"""

import random
import numpy as np

from src.drone import Drone
from src.matcher import match


_MAX_SUB_STEPS = 200  # 每时间步内层迭代上限，防止死循环


def _init_drones(
    n: int, width: int, height: int, seed: int = 0, max_speed: float = float("inf")
) -> list[Drone]:
    """在网格内随机散布 n 架无人机。"""
    rng = random.Random(seed)
    drones = []
    for i in range(n):
        x = rng.uniform(0, width - 1)
        y = rng.uniform(0, height - 1)
        drones.append(Drone(i, x, y, max_speed=max_speed))
    return drones


def run(
    snapshots: list[np.ndarray],
    n_drones: int,
    seed: int = 0,
    verbose: bool = True,
    max_speed: float = float("inf"),
) -> list[list[tuple[float, float]]]:
    """运行多时间步仿真。

    Args:
        snapshots: 快照序列 [S(0), S(1), ..., S(T)]
        n_drones: 无人机数量
        seed: 随机种子
        verbose: 是否打印每步状态
        max_speed: 每子步最大移动距离（inf = 瞬时传送）

    Returns:
        trajectory[t][i] = 第 t 步第 i 架无人机的 (x, y)
    """
    if not snapshots:
        return []

    height, width = snapshots[0].shape
    drones = _init_drones(n_drones, width, height, seed, max_speed=max_speed)
    trajectory: list[list[tuple[float, float]]] = []

    for t, snapshot in enumerate(snapshots):
        # --- 内层收敛循环 ---
        for sub_step in range(_MAX_SUB_STEPS):
            positions = [d.position for d in drones]
            targets = match(snapshot, positions)

            any_moving = False
            for d, (tx, ty) in zip(drones, targets):
                arrived = d.move_toward(tx, ty)
                if not arrived:
                    any_moving = True

            if not any_moving:
                # 所有无人机已到达目标，或无空缺可填
                break

        # 记录轨迹
        step_positions = [d.position for d in drones]
        trajectory.append(step_positions)

        if verbose:
            _print_step(t, snapshot, step_positions, drones)

    return trajectory


def run_single_step(
    snapshot: np.ndarray,
    drone_positions: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """单步仿真：给定快照和当前位置，返回分配后的新位置。"""
    return match(snapshot, drone_positions)


def _print_step(
    t: int,
    snapshot: np.ndarray,
    positions: list[tuple[float, float]],
    drones: list[Drone],
) -> None:
    """打印单步状态摘要。"""
    n_targets = int(np.sum(snapshot))
    n_drones = len(positions)
    in_position = 0
    for dx, dy in positions:
        x, y = int(round(dx)), int(round(dy))
        if 0 <= y < snapshot.shape[0] and 0 <= x < snapshot.shape[1]:
            if snapshot[y, x]:
                in_position += 1
    print(f"--- 时间步 t={t} ---")
    print(f"  目标像素数: {n_targets},  无人机数: {n_drones},  已就位: {in_position}")
    if n_drones <= 10:
        for d in drones:
            print(f"  {d}")
