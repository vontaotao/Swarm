"""
# 1. 功能
最近邻贪心匹配算法（核心模块）。实现无人机群到目标快照的补位分配逻辑。

算法四步：
  Step 1 — 在位检测：如果无人机当前位置落在快照的 True 像素上，
           该像素标记为"已填充"，该无人机不参与分配。
  Step 2 — 空缺收集：收集快照中所有未被填充的 True 像素。
  Step 3 — 距离优先分配：按"最近空缺距离"升序排列未分配无人机，
           贪心匹配到最近的空闲空缺。
  Step 4 — 返回分配结果。

# 2. 输入
- snapshot: 2D 布尔网格 (numpy array, shape=(height, width))
- drone_positions: [(x1, y1), (x2, y2), ...] 无人机当前位置列表

# 3. 输出
- assignments: [(target_x, target_y), ...] 每架无人机的目标位置，
  顺序与输入 drone_positions 一致。已在位的无人机返回原位。

# 4. 核心执行流程
1. 提取快照中所有 True 像素坐标 → 目标集合
2. 检测已在位的无人机，从目标集合中移除对应像素
3. 对剩余无人机，计算到每个剩余目标的距离矩阵
4. 循环：每次选出"最近空缺距离最短"的无人机，分配其最近空缺
5. 从待分配列表中移除该无人机，从空缺集合中移除该像素
6. 重复直到无无人机或无空缺

# 5. 依赖
- numpy
"""

import numpy as np


def match(snapshot: np.ndarray, drone_positions: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """执行一个时间步内的补位匹配。

    Args:
        snapshot: 形状为 (H, W) 的布尔矩阵，True=需要站位
        drone_positions: 无人机当前位置列表 [(x, y), ...]

    Returns:
        每架无人机的目标位置 [(tx, ty), ...]，顺序与输入一致。
    """
    n = len(drone_positions)
    if n == 0:
        return []

    # 提取快照中所有目标像素坐标（浮点化，方便距离计算）
    target_ys, target_xs = np.where(snapshot)
    if len(target_ys) == 0:
        # 没有目标，所有无人机保持不动
        return [pos for pos in drone_positions]

    # 用集合管理空缺像素：(x, y) 键
    vacancies: set[tuple[int, int]] = set(
        (int(x), int(y)) for x, y in zip(target_xs, target_ys)
    )

    # --- Step 1: 在位检测 ---
    assigned: list[tuple[float, float] | None] = [None] * n
    unassigned_indices: list[int] = []

    for i, (dx, dy) in enumerate(drone_positions):
        pixel = (int(round(dx)), int(round(dy)))
        if pixel in vacancies:
            # 无人机已在目标像素上
            assigned[i] = (float(pixel[0]), float(pixel[1]))
            vacancies.remove(pixel)
        else:
            unassigned_indices.append(i)

    # --- Step 2: 空缺收集（vacancies 集合即当前空缺） ---
    # --- Step 3: 距离优先贪心分配 ---
    while unassigned_indices and vacancies:
        vac_list = list(vacancies)  # [(x, y), ...]

        # 找出最近空缺距离最短的无人机
        best_drone_idx: int | None = None
        best_vac: tuple[int, int] | None = None
        best_dist: float = float("inf")

        for i in unassigned_indices:
            dx, dy = drone_positions[i]
            for vx, vy in vac_list:
                dist = (dx - vx) ** 2 + (dy - vy) ** 2  # 平方距离，避免 sqrt
                if dist < best_dist:
                    best_dist = dist
                    best_drone_idx = i
                    best_vac = (vx, vy)

        # 分配
        if best_drone_idx is not None and best_vac is not None:
            assigned[best_drone_idx] = (float(best_vac[0]), float(best_vac[1]))
            unassigned_indices.remove(best_drone_idx)
            vacancies.remove(best_vac)

    # --- Step 4: 未分配到的无人机保持原位 ---
    for i in unassigned_indices:
        assigned[i] = drone_positions[i]

    # 类型安全：此时所有元素都已填充
    return [a for a in assigned]  # type: ignore
