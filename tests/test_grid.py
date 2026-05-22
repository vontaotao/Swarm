"""
# 1. 功能
grid.py 的单元测试。验证四种快照生成函数和辅助函数。

# 2. 输入
- 测试参数（网格尺寸、图案参数）

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 对每种图案类型：生成快照 → 验证形状、数量、边界

# 5. 依赖
- pytest, numpy, src.grid
"""

import numpy as np
import pytest
from src.grid import (
    create_snapshot_rectangle,
    create_snapshot_circle,
    create_snapshot_hollow_circle,
    create_snapshot_custom,
    count_target_cells,
    get_target_positions,
)


class TestSnapshotRectangle:
    def test_basic_rectangle(self):
        grid = create_snapshot_rectangle(100, 100, 50, 50, 10, 6)
        assert grid.shape == (100, 100)
        assert grid.dtype == bool
        # 10x6=60 个 True 像素
        assert count_target_cells(grid) == 60

    def test_rectangle_clipped(self):
        # 矩形部分超出边界，应被裁剪
        grid = create_snapshot_rectangle(10, 10, 0, 0, 6, 6)
        # 只有 (0,0) 到 (2,2) 在边界内 = 3x3 = 9
        assert count_target_cells(grid) == 9


class TestSnapshotCircle:
    def test_basic_circle(self):
        grid = create_snapshot_circle(100, 100, 50, 50, 10)
        assert grid.shape == (100, 100)
        assert count_target_cells(grid) > 0

    def test_center_is_true(self):
        grid = create_snapshot_circle(100, 100, 50, 50, 5)
        assert bool(grid[50, 50]) is True

    def test_corner_is_false(self):
        grid = create_snapshot_circle(100, 100, 50, 50, 5)
        assert bool(grid[0, 0]) is False


class TestSnapshotHollowCircle:
    def test_hollow_ring(self):
        grid = create_snapshot_hollow_circle(100, 100, 50, 50, 5, 10)
        # 内圈应为空
        assert bool(grid[50, 50]) is False
        # 外圈应有像素
        assert bool(grid[50, 40]) is True

    def test_nonzero_count(self):
        grid = create_snapshot_hollow_circle(100, 100, 50, 50, 3, 8)
        assert count_target_cells(grid) > 0


class TestSnapshotCustom:
    def test_custom_points(self):
        points = [(5, 5), (10, 10), (20, 30)]
        grid = create_snapshot_custom(100, 100, points)
        assert count_target_cells(grid) == 3
        assert bool(grid[5, 5]) is True   # grid[y, x]
        assert bool(grid[10, 10]) is True
        assert bool(grid[30, 20]) is True

    def test_points_out_of_bounds_ignored(self):
        points = [(-1, 5), (200, 5)]
        grid = create_snapshot_custom(100, 100, points)
        assert count_target_cells(grid) == 0


class TestHelpers:
    def test_count_target_cells(self):
        grid = np.zeros((10, 10), dtype=bool)
        grid[2, 3] = True
        grid[5, 5] = True
        assert count_target_cells(grid) == 2

    def test_get_target_positions(self):
        grid = np.zeros((10, 10), dtype=bool)
        grid[2, 3] = True
        grid[5, 5] = True
        positions = get_target_positions(grid)
        assert (3, 2) in positions
        assert (5, 5) in positions
        assert len(positions) == 2
