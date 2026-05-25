"""
# 1. 功能
hardware.py 的单元测试。验证 HardwareInterface ABC 和 SimulatedDrone 的行为。

# 2. 输入
- Drone 对象 + 可选的 PhysicsConfig

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试抽象类不能实例化 → 测试 SimulatedDrone 包装 → 测试物理模式

# 5. 依赖
- pytest, src.drone, src.hardware, src.physics
"""

import math
import pytest
from src.drone import Drone
from src.hardware import HardwareInterface, SimulatedDrone
from src.physics import PhysicsConfig


class TestHardwareInterfaceABC:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            HardwareInterface()  # type: ignore


class TestSimulatedDrone:
    def test_wraps_drone_position(self):
        d = Drone(0, 10.0, 20.0, 5.0)
        sd = SimulatedDrone(d)
        assert sd.get_position() == (10.0, 20.0, 5.0)

    def test_wraps_drone_velocity(self):
        d = Drone(0, 0.0, 0.0)
        d.vx = 3.0
        d.vy = 1.5
        d.vz = -2.0
        sd = SimulatedDrone(d)
        assert sd.get_velocity() == (3.0, 1.5, -2.0)

    def test_send_target_and_update_kinematic(self):
        """无物理时，send_target + update 等价于 move_to（max_speed=inf）。"""
        d = Drone(0, 0.0, 0.0, max_speed=float("inf"))
        sd = SimulatedDrone(d)
        sd.send_target(42.0, 99.0, 7.0)
        arrived = sd.update(0.1)
        assert arrived is True
        assert sd.get_position() == (42.0, 99.0, 7.0)

    def test_update_no_target(self):
        """未设置目标时 update 返回 True。"""
        d = Drone(0, 0.0, 0.0)
        sd = SimulatedDrone(d)
        assert sd.update(0.1) is True

    def test_physics_mode_smooth_movement(self):
        """有物理限制时轨迹平滑而非瞬时到达。"""
        d = Drone(0, 0.0, 0.0, max_speed=2.0)
        cfg = PhysicsConfig(dt=0.1, max_accel=5.0)
        sd = SimulatedDrone(d, physics=cfg)
        sd.send_target(100.0, 0.0, 0.0)
        positions = []
        for _ in range(20):
            sd.update(0.1)
            positions.append(sd.get_position()[0])
        # 速度受限，20步后不应到达100
        assert positions[-1] < 100.0
        # 轨迹单调递增
        for i in range(1, len(positions)):
            assert positions[i] > positions[i - 1]

    def test_repr_includes_info(self):
        d = Drone(5, 1.0, 2.0)
        sd = SimulatedDrone(d)
        r = repr(sd)
        assert "SimulatedDrone" in r
        assert "kinematic" in r

    def test_repr_physics_mode(self):
        d = Drone(5, 1.0, 2.0)
        sd = SimulatedDrone(d, physics=PhysicsConfig())
        r = repr(sd)
        assert "physics" in r

    def test_multiple_drones_independent(self):
        d1 = Drone(0, 0.0, 0.0, max_speed=float("inf"))
        d2 = Drone(1, 10.0, 10.0, max_speed=float("inf"))
        sd1 = SimulatedDrone(d1)
        sd2 = SimulatedDrone(d2)
        sd1.send_target(5.0, 5.0, 0.0)
        sd2.send_target(15.0, 15.0, 0.0)
        sd1.update(0.1)
        sd2.update(0.1)
        assert sd1.get_position() == (5.0, 5.0, 0.0)
        assert sd2.get_position() == (15.0, 15.0, 0.0)
