"""
# 1. 功能
matcher.py 的单元测试。验证补位匹配算法的每种边界情况。

# 2. 输入
- 构造的目标快照和无人机位置

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 覆盖：空输入、全在位、简单一对一、多对多竞争、不对称数量

# 5. 依赖
- pytest, numpy, src.matcher, src.grid
"""

import numpy as np
from src.matcher import match


class TestMatchEmpty:
    def test_no_drones(self):
        grid = np.array([[True]], dtype=bool)
        result = match(grid, [])
        assert result == []

    def test_no_targets(self):
        grid = np.zeros((10, 10), dtype=bool)
        positions = [(1.0, 1.0), (2.0, 2.0)]
        result = match(grid, positions)
        # 无目标，保持原位
        assert result == positions


class TestMatchAlreadyInPosition:
    def test_all_in_position(self):
        # 两个目标像素，两架无人机正好在上面
        grid = np.zeros((10, 10), dtype=bool)
        grid[2, 3] = True
        grid[5, 5] = True
        positions = [(3.0, 2.0), (5.0, 5.0)]
        result = match(grid, positions)
        assert (3.0, 2.0) in result
        assert (5.0, 5.0) in result
        assert len(result) == 2


class TestMatchSimpleAssignment:
    def test_one_drone_one_vacancy(self):
        grid = np.zeros((10, 10), dtype=bool)
        grid[5, 8] = True
        positions = [(0.0, 0.0)]
        result = match(grid, positions)
        assert result == [(8.0, 5.0)]

    def test_two_drones_two_vacancies(self):
        grid = np.zeros((10, 10), dtype=bool)
        grid[0, 0] = True  # 目标是 (0, 0)
        grid[0, 9] = True  # 目标是 (9, 0)
        positions = [(0.0, 0.0), (9.0, 0.0)]
        result = match(grid, positions)
        assert set(result) == {(0.0, 0.0), (9.0, 0.0)}


class TestMatchPriority:
    def test_closer_drone_gets_nearby_vacancy(self):
        """距离近的无人机优先分配最近的空缺。"""
        grid = np.zeros((20, 20), dtype=bool)
        # 两个目标点： (5,5) 和 (15,5)
        grid[5, 5] = True
        grid[5, 15] = True
        # drone_0 在 (0,0)，距 (5,5) 近
        # drone_1 在 (10,0)，距 (15,5) 近
        positions = [(0.0, 0.0), (10.0, 0.0)]
        result = match(grid, positions)
        # drone_0 最近空缺距离更短(≈7.07 vs ≈5.39)，但 drone_1 到 (15,5) 距离 ≈7.07
        # 所以 drone_0 应该得到 (5,5), drone_1 得到 (15,5)
        assert result[0] == (5.0, 5.0)
        assert result[1] == (15.0, 5.0)


class TestMatchAsymmetric:
    def test_more_drones_than_vacancies(self):
        """无人机多于目标，多余的保持原位。"""
        grid = np.zeros((10, 10), dtype=bool)
        grid[0, 0] = True
        positions = [(0.0, 0.0), (5.0, 5.0), (8.0, 8.0)]
        result = match(grid, positions)
        # 只一个目标 (0,0)，已有无人机在 (0,0)
        assert (0.0, 0.0) in result
        # 其他保持原位
        assert (5.0, 5.0) in result
        assert (8.0, 8.0) in result
        assert len(result) == 3

    def test_more_vacancies_than_drones(self):
        """空缺多于无人机，所有无人机都被分配。"""
        grid = np.zeros((20, 20), dtype=bool)
        grid[2, 2] = True
        grid[2, 5] = True
        grid[2, 8] = True
        grid[2, 12] = True
        positions = [(2.0, 3.0), (8.0, 2.0)]
        result = match(grid, positions)
        assert len(result) == 2
        # 两架都应在目标像素上
        for tx, ty in result:
            assert grid[int(ty), int(tx)] is np.True_


class TestMatchRoundToPixel:
    def test_drone_near_target_pixel(self):
        """无人机位置浮点化后四舍五入匹配像素。"""
        grid = np.zeros((10, 10), dtype=bool)
        grid[3, 3] = True
        # 无人机在 (3.2, 2.8)，四舍五入为 (3, 3) 像素
        positions = [(3.2, 2.8)]
        result = match(grid, positions)
        assert result == [(3.0, 3.0)]
