"""
# 1. 功能
2D 空间网格模块。定义离散化的二维仿真空间，并提供目标快照（编队图案）的生成函数。
"快照"就是一个布尔矩阵：True 表示该像素需要一架无人机站位，False 表示空。

# 2. 输入
- 网格尺寸 (width, height)
- 图案参数（中心坐标、半径、宽高等）

# 3. 输出
- 布尔网格矩阵 (numpy 2D array, shape=(height, width), dtype=bool)

# 4. 核心执行流程
- 根据图案类型调用对应的生成函数
- 生成函数在矩阵上标记 True 像素
- 返回完整的布尔矩阵

# 5. 依赖
- numpy
"""

import numpy as np


def create_snapshot_rectangle(
    width: int, height: int, cx: int, cy: int, rect_w: int, rect_h: int
) -> np.ndarray:
    """生成矩形编队快照。

    Args:
        width: 网格宽度
        height: 网格高度
        cx: 矩形中心 x 坐标
        cy: 矩形中心 y 坐标
        rect_w: 矩形宽度
        rect_h: 矩形高度
    """
    grid = np.zeros((height, width), dtype=bool)
    x0 = max(0, cx - rect_w // 2)
    y0 = max(0, cy - rect_h // 2)
    x1 = min(width, cx + rect_w // 2)
    y1 = min(height, cy + rect_h // 2)
    grid[y0:y1, x0:x1] = True
    return grid


def create_snapshot_circle(
    width: int, height: int, cx: int, cy: int, radius: int
) -> np.ndarray:
    """生成圆形编队快照。

    Args:
        width: 网格宽度
        height: 网格高度
        cx: 圆心 x 坐标
        cy: 圆心 y 坐标
        radius: 半径（像素）
    """
    grid = np.zeros((height, width), dtype=bool)
    yy, xx = np.ogrid[:height, :width]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    grid[dist <= radius] = True
    return grid


def create_snapshot_hollow_circle(
    width: int, height: int, cx: int, cy: int, inner_radius: int, outer_radius: int
) -> np.ndarray:
    """生成空心圆环编队快照。

    Args:
        width: 网格宽度
        height: 网格高度
        cx: 圆心 x 坐标
        cy: 圆心 y 坐标
        inner_radius: 内半径
        outer_radius: 外半径
    """
    grid = np.zeros((height, width), dtype=bool)
    yy, xx = np.ogrid[:height, :width]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    grid[(dist >= inner_radius) & (dist <= outer_radius)] = True
    return grid


def create_snapshot_custom(width: int, height: int, points: list[tuple[int, int]]) -> np.ndarray:
    """根据自定义点位列表生成快照。

    Args:
        width: 网格宽度
        height: 网格高度
        points: [(x1, y1), (x2, y2), ...] 目标点位列表
    """
    grid = np.zeros((height, width), dtype=bool)
    for x, y in points:
        if 0 <= x < width and 0 <= y < height:
            grid[y, x] = True
    return grid


def create_snapshot_box(
    width: int, height: int, depth: int,
    cx: int, cy: int, cz: int,
    box_w: int, box_h: int, box_d: int,
) -> np.ndarray:
    """生成 3D 长方体编队快照。

    Args:
        width, height, depth: 网格尺寸
        cx, cy, cz: 长方体中心坐标
        box_w, box_h, box_d: 长方体宽高深
    """
    grid = np.zeros((depth, height, width), dtype=bool)
    x0 = max(0, cx - box_w // 2)
    y0 = max(0, cy - box_h // 2)
    z0 = max(0, cz - box_d // 2)
    x1 = min(width, cx + box_w // 2)
    y1 = min(height, cy + box_h // 2)
    z1 = min(depth, cz + box_d // 2)
    grid[z0:z1, y0:y1, x0:x1] = True
    return grid


def create_snapshot_sphere(
    width: int, height: int, depth: int,
    cx: int, cy: int, cz: int, radius: int,
) -> np.ndarray:
    """生成 3D 球体编队快照。

    Args:
        width, height, depth: 网格尺寸
        cx, cy, cz: 球心坐标
        radius: 半径（像素）
    """
    grid = np.zeros((depth, height, width), dtype=bool)
    zz, yy, xx = np.ogrid[:depth, :height, :width]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2 + (zz - cz) ** 2)
    grid[dist <= radius] = True
    return grid


def count_target_cells(grid: np.ndarray) -> int:
    """统计快照中需要填充的目标像素数。"""
    return int(np.sum(grid))


def get_target_positions(grid: np.ndarray) -> list[tuple[int, ...]]:
    """提取快照中所有目标像素的坐标列表。

    Returns:
        坐标列表，维度自动适配。2D: [(x, y), ...], 3D: [(x, y, z), ...]
    """
    idx_arrays = np.where(grid)
    n_cells = len(idx_arrays[0])
    positions = []
    for i in range(n_cells):
        coord = tuple(int(idx_arrays[d][i]) for d in reversed(range(len(idx_arrays))))
        positions.append(coord)
    return positions
