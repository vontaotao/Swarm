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
import pytest
from src.drone import Drone


class TestDroneInit:
    def test_init(self):
        d = Drone(0, 10.0, 20.0)
        assert d.id == 0
        assert d.x == 10.0
        assert d.y == 20.0

    def test_position_property(self):
        d = Drone(1, 5.5, 6.5)
        assert d.position == (5.5, 6.5, 0.0)

    def test_init_with_z(self):
        d = Drone(2, 1.0, 2.0, 3.0)
        assert d.position == (1.0, 2.0, 3.0)
        assert d.z == 3.0


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
        assert d.position == (-5.0, -3.0, 0.0)

    def test_move_to_3d(self):
        d = Drone(0, 0.0, 0.0, 0.0)
        d.move_to(10.0, 20.0, 30.0)
        assert d.position == (10.0, 20.0, 30.0)


class TestDroneMoveToward:
    def test_already_at_target_returns_true(self):
        d = Drone(0, 5.0, 5.0, max_speed=1.0)
        arrived = d.move_toward(5.0, 5.0)
        assert arrived is True
        assert d.position == (5.0, 5.0, 0.0)

    def test_close_target_arrives(self):
        """目标在 max_speed 范围内，一步到达。"""
        d = Drone(0, 0.0, 0.0, max_speed=5.0)
        arrived = d.move_toward(3.0, 4.0)  # 距离 5 ≤ max_speed
        assert arrived is True
        assert d.position == (3.0, 4.0, 0.0)

    def test_far_target_steps(self):
        """目标超出 max_speed，只移动一步。"""
        d = Drone(0, 0.0, 0.0, max_speed=3.0)
        arrived = d.move_toward(30.0, 0.0)  # 距离 30 > 3
        assert arrived is False
        assert d.x == pytest.approx(3.0)
        assert d.y == pytest.approx(0.0)

    def test_far_target_multiple_steps(self):
        """多次调用最终到达。"""
        d = Drone(0, 0.0, 0.0, max_speed=2.0)
        step1 = d.move_toward(6.0, 0.0)  # 移 2
        assert step1 is False
        step2 = d.move_toward(6.0, 0.0)  # 移 2
        assert step2 is False
        step3 = d.move_toward(6.0, 0.0)  # 剩下 2 ≤ max_speed，到达
        assert step3 is True
        assert d.position == (6.0, 0.0, 0.0)

    def test_infinite_speed_arrives_immediately(self):
        """max_speed=inf 时等价于 move_to。"""
        d = Drone(0, 0.0, 0.0)
        arrived = d.move_toward(100.0, 200.0)
        assert arrived is True
        assert d.position == (100.0, 200.0, 0.0)

    def test_move_toward_3d(self):
        """move_toward 支持 z 轴。"""
        d = Drone(0, 0.0, 0.0, 0.0, max_speed=3.0)
        # 距离 sqrt(1+4+4)=3，刚好到达
        arrived = d.move_toward(1.0, 2.0, 2.0)
        assert arrived is True
        assert d.position == (1.0, 2.0, 2.0)

    def test_distance_3d(self):
        d = Drone(0, 0.0, 0.0, 0.0)
        assert math.isclose(d.distance_to(1.0, 2.0, 2.0), 3.0)


class TestDroneRepr:
    def test_repr(self):
        d = Drone(7, 1.5, 2.5)
        r = repr(d)
        assert "7" in r
        assert "1.5" in r
        assert "2.5" in r


class TestDronePhysics:
    def test_default_physics_params(self):
        d = Drone(0, 0.0, 0.0)
        assert d.max_accel == float("inf")
        assert d.drag == 0.0
        assert d.mass == 1.0
        assert d.vx == 0.0 and d.vy == 0.0 and d.vz == 0.0

    def test_physics_params_in_init(self):
        d = Drone(1, 1.0, 2.0, 3.0, max_accel=5.0, drag=0.1, mass=2.0)
        assert d.max_accel == 5.0
        assert d.drag == 0.1
        assert d.mass == 2.0

    def test_velocity_property(self):
        d = Drone(0, 0.0, 0.0)
        assert d.velocity == (0.0, 0.0, 0.0)
        d.vx = 3.0
        d.vy = -1.0
        d.vz = 2.5
        assert d.velocity == (3.0, -1.0, 2.5)

    def test_set_target(self):
        d = Drone(0, 0.0, 0.0)
        d.set_target(10.0, 20.0, 5.0)
        assert d._target == (10.0, 20.0, 5.0)

    def test_set_target_2d_default_z(self):
        d = Drone(0, 0.0, 0.0)
        d.set_target(7.0, 8.0)
        assert d._target == (7.0, 8.0, 0.0)
