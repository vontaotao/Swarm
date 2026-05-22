"""
# 1. 功能
最近邻贪心匹配算法（核心模块）。实现无人机群到目标快照的补位分配逻辑。
支持 2D 和 3D 快照，维度自动适配。

算法四步：
  Step 1 — 在位检测：如果无人机当前位置落在快照的 True 像素上，
           该像素标记为"已填充"，该无人机不参与分配。
  Step 2 — 空缺收集：收集快照中所有未被填充的 True 像素。
  Step 3 — 距离优先分配：按"最近空缺距离"升序排列未分配无人机，
           贪心匹配到最近的空闲空缺。
  Step 4 — 返回分配结果。

# 2. 输入
- snapshot: 布尔网格 (numpy array, shape=(height, width) 或 (depth, height, width))
- drone_positions: 无人机当前位置列表 [(x, y), ...] 或 [(x, y, z), ...]

# 3. 输出
- assignments: 每架无人机的目标位置，顺序与输入一致，维度与输入一致

# 4. 核心执行流程
1. 提取快照中所有 True 像素坐标 → 目标集合
2. 检测已在位的无人机，从目标集合中移除对应像素
3. 对剩余无人机，计算到每个剩余目标的平方距离
4. 循环：每次选出"最近空缺距离最短"的无人机，分配其最近空缺
5. 重复直到无无人机或无空缺

# 5. 依赖
- numpy
"""

import numpy as np


def _sq_dist(a: tuple[float, ...], b: tuple[int, ...]) -> float:
    """平方欧几里得距离，支持任意维度。"""
    return sum((ai - bi) ** 2 for ai, bi in zip(a, b))


def _vacancies_from_snapshot(snapshot: np.ndarray) -> set[tuple[int, ...]]:
    """从布尔快照提取目标像素坐标集合。坐标序为 (x, y, ...)。"""
    idx_arrays = np.where(snapshot)  # (row, col) or (depth, row, col)
    n_cells = len(idx_arrays[0])
    coords: list[tuple[int, ...]] = []
    for i in range(n_cells):
        # idx_arrays 是 C-order (z, y, x)，反转为 (x, y, z)
        coord = tuple(int(idx_arrays[d][i]) for d in reversed(range(len(idx_arrays))))
        coords.append(coord)
    return set(coords)


def _pixel_at(pos: tuple[float, ...]) -> tuple[int, ...]:
    """将浮点位置四舍五入为像素坐标。"""
    return tuple(int(round(c)) for c in pos)


def match(snapshot: np.ndarray, drone_positions: list[tuple[float, ...]]) -> list[tuple[float, ...]]:
    """执行一个时间步内的补位匹配。

    Args:
        snapshot: 布尔矩阵，True=需要站位
        drone_positions: 无人机当前位置列表 [(x, y), ...] 或 [(x, y, z), ...]

    Returns:
        每架无人机的目标位置，顺序与输入一致。
    """
    n = len(drone_positions)
    if n == 0:
        return []

    vacancies = _vacancies_from_snapshot(snapshot)
    if not vacancies:
        return [pos for pos in drone_positions]

    # --- Step 1: 在位检测 ---
    assigned: list[tuple[float, ...] | None] = [None] * n
    unassigned_indices: list[int] = []

    for i, pos in enumerate(drone_positions):
        pixel = _pixel_at(pos)
        if pixel in vacancies:
            assigned[i] = tuple(float(c) for c in pixel)
            vacancies.remove(pixel)
        else:
            unassigned_indices.append(i)

    # --- Step 2 & 3: 距离优先贪心分配 ---
    while unassigned_indices and vacancies:
        vac_list = list(vacancies)

        best_drone_idx: int | None = None
        best_vac: tuple[int, ...] | None = None
        best_dist: float = float("inf")

        for i in unassigned_indices:
            pos = drone_positions[i]
            for vac in vac_list:
                dist = _sq_dist(pos, vac)
                if dist < best_dist:
                    best_dist = dist
                    best_drone_idx = i
                    best_vac = vac

        if best_drone_idx is not None and best_vac is not None:
            assigned[best_drone_idx] = tuple(float(c) for c in best_vac)
            unassigned_indices.remove(best_drone_idx)
            vacancies.remove(best_vac)

    # --- Step 4: 未分配到的无人机保持原位 ---
    for i in unassigned_indices:
        assigned[i] = drone_positions[i]

    return [a for a in assigned]  # type: ignore
