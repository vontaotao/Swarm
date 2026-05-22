"""
# 1. 功能
drone.py 的单元测试。验证无人机的初始化、距离计算和移动。

# 2. 输入
- 测试参数（ID、坐标、目标点）

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试初始化 → 测试距离计算 → 测试移动 → 测试位置属性

# 5. 依赖
- pytest, src.drone
"""

import math
from src.drone import Drone


class TestDroneInit:
    def test_init(self):
        d = Drone(0, 10.0, 20.0)
        assert d.id == 0
        assert d.x == 10.0
        assert d.y == 20.0

    def test_position_property(self):
        d = Drone(1, 5.5, 6.5)
        assert d.position == (5.5, 6.5)


class TestDroneDistance:
    def test_distance_to_self(self):
        d = Drone(0, 10.0, 20.0)
        assert d.distance_to(10.0, 20.0) == 0.0

    def test_distance_horizontal(self):
        d = Drone(0, 0.0, 0.0)
        assert d.distance_to(3.0, 0.0) == 3.0

    def test_distance_vertical(self):
        d = Drone(0, 0.0, 0.0)
        assert d.distance_to(0.0, 4.0) == 4.0

    def test_distance_diagonal(self):
        d = Drone(0, 0.0, 0.0)
        assert math.isclose(d.distance_to(3.0, 4.0), 5.0)


class TestDroneMove:
    def test_move_to(self):
        d = Drone(0, 0.0, 0.0)
        d.move_to(42.0, 99.0)
        assert d.x == 42.0
        assert d.y == 99.0

    def test_move_to_negative(self):
        d = Drone(0, 10.0, 10.0)
        d.move_to(-5.0, -3.0)
        assert d.position == (-5.0, -3.0)


class TestDroneRepr:
    def test_repr(self):
        d = Drone(7, 1.5, 2.5)
        r = repr(d)
        assert "7" in r
        assert "1.5" in r
        assert "2.5" in r
