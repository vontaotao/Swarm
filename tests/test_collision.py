"""
# 1. 功能
collision.py 的单元测试。验证碰撞检测、排斥力计算和规避函数。

# 2. 输入
- Drone 对象列表

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试检测 → 测试排斥力 → 测试规避 → 测试 3D

# 5. 依赖
- pytest, math, src.drone, src.collision
"""

import math
import pytest
from src.drone import Drone
from src.collision import detect_collisions, compute_repulsion, avoid_collisions


class TestDetectCollisions:
    def test_no_collision_when_far(self):
        drones = [Drone(0, 0.0, 0.0), Drone(1, 10.0, 0.0)]
        pairs = detect_collisions(drones, min_distance=2.0)
        assert pairs == []

    def test_collision_when_close(self):
        drones = [Drone(0, 0.0, 0.0), Drone(1, 0.5, 0.0)]
        pairs = detect_collisions(drones, min_distance=2.0)
        assert len(pairs) == 1
        assert pairs[0] == (0, 1)

    def test_exactly_at_boundary(self):
        """距离等于 min_distance 不视为碰撞。"""
        drones = [Drone(0, 0.0, 0.0), Drone(1, 2.0, 0.0)]
        pairs = detect_collisions(drones, min_distance=2.0)
        assert pairs == []

    def test_multiple_pairs(self):
        drones = [
            Drone(0, 0.0, 0.0),
            Drone(1, 0.5, 0.0),
            Drone(2, 3.0, 0.0),
        ]
        pairs = detect_collisions(drones, min_distance=2.0)
        assert len(pairs) == 1  # 只有 0-1 在范围内

    def test_3d_detection(self):
        drones = [Drone(0, 0.0, 0.0, 0.0), Drone(1, 1.0, 1.0, 1.0)]
        # 距离 sqrt(3) ≈ 1.73
        pairs = detect_collisions(drones, min_distance=2.0)
        assert len(pairs) == 1


class TestComputeRepulsion:
    def test_direction_away_from_neighbor(self):
        d1 = Drone(0, 0.0, 0.0)
        d2 = Drone(1, 1.0, 0.0)
        fx, fy, fz = compute_repulsion(d1, d2, min_distance=2.0, strength=1.0)
        # d1 在 0, d2 在 +1 → 方向从 d2 指向 d1 是 -x
        assert fx < 0
        assert fy == 0.0

    def test_magnitude_inverse_distance(self):
        d1 = Drone(0, 0.0, 0.0)
        d_near = Drone(1, 0.3, 0.0)
        d_far = Drone(2, 1.5, 0.0)
        fx_near, _, _ = compute_repulsion(d1, d_near, min_distance=2.0, strength=1.0)
        fx_far, _, _ = compute_repulsion(d1, d_far, min_distance=2.0, strength=1.0)
        # 越近力越大
        assert abs(fx_near) > abs(fx_far)

    def test_zero_when_far(self):
        d1 = Drone(0, 0.0, 0.0)
        d2 = Drone(1, 10.0, 0.0)
        fx, fy, fz = compute_repulsion(d1, d2, min_distance=2.0, strength=1.0)
        assert (fx, fy, fz) == (0.0, 0.0, 0.0)


class TestAvoidCollisions:
    def test_modifies_velocity(self):
        drones = [Drone(0, 0.0, 0.0), Drone(1, 0.5, 0.0)]
        count = avoid_collisions(drones, min_distance=2.0, strength=1.0)
        assert count == 1
        # d0 被推开（vx 变为负值）
        assert drones[0].vx < 0

    def test_returns_collision_count(self):
        drones = [Drone(0, 0.0, 0.0), Drone(1, 0.5, 0.0), Drone(2, 10.0, 0.0)]
        count = avoid_collisions(drones, min_distance=2.0)
        assert count == 1

    def test_momentum_conservation(self):
        """排斥力等大反向，总速度增量为零。"""
        drones = [Drone(0, 0.0, 0.0), Drone(1, 0.5, 0.0)]
        avoid_collisions(drones, min_distance=2.0, strength=1.0)
        total_vx = drones[0].vx + drones[1].vx
        total_vy = drones[0].vy + drones[1].vy
        assert math.isclose(total_vx, 0.0, abs_tol=1e-9)
        assert math.isclose(total_vy, 0.0, abs_tol=1e-9)
