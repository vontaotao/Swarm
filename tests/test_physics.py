"""
# 1. 功能
physics.py 的单元测试。验证物理学步进、收敛、阻力、质量和加速度约束。

# 2. 输入
- Drone 对象 + PhysicsConfig

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试默认配置 → 测试加速度限制 → 测试阻力 → 测试 3D → 测试收敛

# 5. 依赖
- pytest, src.drone, src.physics
"""

import math
import pytest
from src.drone import Drone
from src.physics import PhysicsConfig, physics_step


class TestPhysicsConfig:
    def test_defaults(self):
        cfg = PhysicsConfig()
        assert cfg.max_accel == float("inf")
        assert cfg.drag == 0.0
        assert cfg.mass == 1.0
        assert cfg.dt == 0.1

    def test_custom_values(self):
        cfg = PhysicsConfig(max_accel=5.0, drag=0.2, mass=2.0, dt=0.05)
        assert cfg.max_accel == 5.0
        assert cfg.drag == 0.2
        assert cfg.mass == 2.0
        assert cfg.dt == 0.05


class TestPhysicsStep:
    def test_no_limit_instant(self):
        """max_accel=inf 时，physics_step 等价于快速移动。"""
        d = Drone(0, 0.0, 0.0, max_speed=float("inf"))
        cfg = PhysicsConfig()
        arrived = physics_step(d, 5.0, 0.0, 0.0, cfg)
        assert arrived is True
        assert d.position == (5.0, 0.0, 0.0)

    def test_accel_limit_ramp(self):
        """有限加速度时，速度逐步增加而非瞬时达到 max_speed。"""
        d = Drone(0, 0.0, 0.0, max_speed=10.0, max_accel=20.0)
        cfg = PhysicsConfig(dt=0.1)
        # dt=0.1, max_accel=20 -> 单步最大速度增量 = 20*0.1 = 2.0
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # 第1步速度应该远小于 max_speed=10
        assert abs(d.vx) <= 2.1  # 允许浮点误差

    def test_drag_decay(self):
        """有阻力时，无目标速度衰减。"""
        d = Drone(0, 0.0, 0.0, drag=0.5)
        d.vx = 10.0
        cfg = PhysicsConfig(drag=0.5, dt=0.1)
        # 无目标：期望速度=0，纯阻力减速
        # a_x = -drag * vx = -5.0, dv = a*dt = -0.5
        physics_step(d, 0.0, 0.0, 0.0, cfg)
        assert d.vx < 10.0  # 速度下降了

    def test_arrival_zero_velocity(self):
        """到达目标时速度被清零。"""
        d = Drone(0, 5.0, 0.0, max_speed=float("inf"))
        d.vx = 0.5
        cfg = PhysicsConfig()
        arrived = physics_step(d, 5.0, 0.0, 0.0, cfg)
        assert arrived is True
        assert d.vx == 0.0

    def test_3d_physics(self):
        """z 轴参与加速和移动。"""
        d = Drone(0, 0.0, 0.0, 0.0, max_speed=float("inf"))
        cfg = PhysicsConfig()
        arrived = physics_step(d, 3.0, 4.0, 5.0, cfg)
        assert arrived is True
        assert d.position == (3.0, 4.0, 5.0)

    def test_mass_effect(self):
        """质量翻倍则同力下加速度减半。"""
        d_light = Drone(0, 0.0, 0.0, max_speed=5.0, mass=1.0)
        d_heavy = Drone(1, 0.0, 0.0, max_speed=5.0, mass=2.0)
        cfg = PhysicsConfig(dt=0.1, max_accel=10.0)
        physics_step(d_light, 100.0, 0.0, 0.0, cfg)
        physics_step(d_heavy, 100.0, 0.0, 0.0, cfg)
        # 质量大的无人机速度增量应更小
        assert abs(d_heavy.vx) < abs(d_light.vx)

    def test_direction_toward_target(self):
        """速度方向指向目标。"""
        d = Drone(0, 0.0, 0.0, max_speed=10.0, max_accel=50.0)
        cfg = PhysicsConfig(dt=0.1)
        physics_step(d, 10.0, 0.0, 0.0, cfg)
        assert d.vx > 0
        # y, z 方向无偏差
        assert d.vy == 0.0
        assert d.vz == 0.0


class TestPhysicsConvergence:
    def test_multi_step_converges(self):
        """多次 physics_step 最终到达目标。"""
        d = Drone(0, 0.0, 0.0, max_speed=2.0, max_accel=10.0)
        cfg = PhysicsConfig(dt=0.1)
        for _ in range(100):
            arrived = physics_step(d, 6.0, 0.0, 0.0, cfg)
            if arrived:
                break
        assert arrived is True
        assert d.x == pytest.approx(6.0)
        assert d.y == pytest.approx(0.0)
        assert d.z == pytest.approx(0.0)

    def test_speed_limit_respected(self):
        """速度不超过 max_speed。"""
        d = Drone(0, 0.0, 0.0, max_speed=3.0, max_accel=100.0)
        cfg = PhysicsConfig(dt=0.05)
        for _ in range(50):
            physics_step(d, 100.0, 0.0, 0.0, cfg)
            speed = math.sqrt(d.vx * d.vx + d.vy * d.vy + d.vz * d.vz)
            assert speed <= 3.0 + 1e-9


class TestPhysicsPriority:
    """验证 physics_step 中 config 优先、drone 回退的规则。"""

    def test_config_mass_overrides_drone(self):
        d = Drone(0, 0.0, 0.0, max_speed=5.0, mass=2.0)
        cfg = PhysicsConfig(dt=0.1, max_accel=10.0, mass=4.0)
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # config.mass=4.0 生效，加速度更小
        assert abs(d.vx) < 1.0

    def test_drone_mass_wins_when_config_default(self):
        d = Drone(0, 0.0, 0.0, max_speed=5.0, mass=10.0)
        cfg = PhysicsConfig(dt=0.1, max_accel=10.0)  # mass 默认 1.0
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # drone.mass=10.0 生效
        assert abs(d.vx) < 0.2

    def test_config_drag_overrides_drone(self):
        d = Drone(0, 0.0, 0.0, drag=0.1)
        d.vx = 10.0
        cfg = PhysicsConfig(dt=0.1, drag=2.0)  # 显式传入
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # config.drag=2.0 生效 → 强阻力
        assert d.vx < 5.0

    def test_drone_drag_wins_when_config_default(self):
        d = Drone(0, 0.0, 0.0, drag=0.8)
        d.vx = 10.0
        cfg = PhysicsConfig(dt=0.1)  # drag 默认 0.0
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # drone.drag=0.8 生效
        assert d.vx < 10.0

    def test_config_accel_overrides_drone(self):
        d = Drone(0, 0.0, 0.0, max_speed=10.0, max_accel=50.0)
        cfg = PhysicsConfig(dt=0.1, max_accel=2.0)  # 显式传入
        physics_step(d, 100.0, 0.0, 0.0, cfg)
        # config.max_accel=2.0 生效，单步最大速度增量 2*0.1=0.2
        assert abs(d.vx) <= 0.21


class TestPhysicsEdgeCases:
    """物理引擎边界情况测试。"""

    def test_tiny_dist_nonzero_speed(self):
        """距离极小 (< 1e-9) 但速度非零时，速度清零并返回 True。"""
        d = Drone(0, 5.0, 0.0, max_speed=float("inf"))
        d.vx = 3.0
        d.vy = 1.0
        cfg = PhysicsConfig()
        arrived = physics_step(d, 5.0000000001, 0.0, 0.0, cfg)
        assert arrived is True
        assert d.vx == 0.0
        assert d.vy == 0.0
