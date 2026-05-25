"""
# 1. 功能
simulation.py 的单元和集成测试。验证零步、单步、多步仿真的正确性。

# 2. 输入
- 构造的快照序列和无人机位置

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试空快照序列、单步仿真、多步仿真收敛性

# 5. 依赖
- pytest, numpy, src.simulation, src.grid
"""

import numpy as np
from src.simulation import run, run_single_step
from src.grid import create_snapshot_rectangle


class TestRunEmpty:
    def test_empty_snapshots(self):
        result = run([], n_drones=5, verbose=False)
        assert result == []


class TestRunSingleStep:
    def test_single_step_api(self):
        snapshot = np.zeros((10, 10), dtype=bool)
        snapshot[0, 5] = True  # 目标 (5, 0)
        positions = [(0.0, 0.0)]
        result = run_single_step(snapshot, positions)
        assert result == [(5.0, 0.0)]

    def test_single_step_no_move_when_on_target(self):
        snapshot = np.zeros((10, 10), dtype=bool)
        snapshot[3, 3] = True
        positions = [(3.0, 3.0)]
        result = run_single_step(snapshot, positions)
        assert result == [(3.0, 3.0)]


class TestRunMultiStep:
    def test_two_steps(self):
        snapshots = [
            create_snapshot_rectangle(20, 20, 5, 5, 4, 4),   # t=0
            create_snapshot_rectangle(20, 20, 15, 15, 4, 4),  # t=1
        ]
        trajectory = run(snapshots, n_drones=10, seed=42, verbose=False)
        assert len(trajectory) == 2
        for step in trajectory:
            assert len(step) == 10

    def test_trajectory_shape(self):
        """泛化测试：轨迹维度正确。"""
        snapshots = [
            create_snapshot_rectangle(30, 30, 10, 10, 6, 6),
            create_snapshot_rectangle(30, 30, 10, 20, 6, 6),
            create_snapshot_rectangle(30, 30, 20, 10, 6, 6),
        ]
        trajectory = run(snapshots, n_drones=20, seed=1, verbose=False)
        assert len(trajectory) == 3
        for step in trajectory:
            assert len(step) == 20
            for x, y, z in step:
                assert 0.0 <= x < 30.0
                assert 0.0 <= y < 30.0
                assert z == 0.0

    def test_all_drones_reach_targets(self):
        """当目标像素足够多时，所有无人机都应到达目标位置。"""
        snapshot = create_snapshot_rectangle(50, 50, 25, 25, 20, 20)  # 400 个目标
        snapshots = [snapshot] * 3  # 静态快照，多次迭代
        trajectory = run(snapshots, n_drones=30, seed=0, verbose=False)
        final = trajectory[-1]
        for x, y, z in final:
            ix, iy = int(round(x)), int(round(y))
            assert snapshot[iy, ix] is np.True_


class TestRunWithSpeedLimit:
    def test_max_speed_infinite_behavior_same(self):
        """max_speed=inf 应与原始行为一致（瞬时到达）。"""
        snapshots = [
            create_snapshot_rectangle(30, 30, 10, 10, 6, 6),
            create_snapshot_rectangle(30, 30, 20, 20, 6, 6),
        ]
        traj_inf = run(snapshots, n_drones=10, seed=42, max_speed=float("inf"), verbose=False)
        traj_default = run(snapshots, n_drones=10, seed=42, verbose=False)
        assert len(traj_inf) == len(traj_default)
        for step_a, step_b in zip(traj_inf, traj_default):
            for (xa, ya, za), (xb, yb, zb) in zip(step_a, step_b):
                assert xa == xb
                assert ya == yb

    def test_speed_limit_does_not_break_convergence(self):
        """速度有限时，静态快照下最终仍应收敛。"""
        snapshot = create_snapshot_rectangle(40, 40, 20, 20, 10, 8)
        snapshots = [snapshot] * 3
        trajectory = run(snapshots, n_drones=8, seed=7, max_speed=2.0, verbose=False)
        final = trajectory[-1]
        for x, y, z in final:
            ix, iy = int(round(x)), int(round(y))
            assert snapshot[iy, ix] is np.True_

    def test_speed_limit_produces_trajectory(self):
        """速度有限时轨迹维度正确。"""
        snapshots = [
            create_snapshot_rectangle(20, 20, 5, 5, 4, 4),
            create_snapshot_rectangle(20, 20, 15, 15, 4, 4),
        ]
        trajectory = run(snapshots, n_drones=6, seed=99, max_speed=3.0, verbose=False)
        assert len(trajectory) == 2
        for step in trajectory:
            assert len(step) == 6
            for x, y, z in step:
                assert 0.0 <= x < 20.0
                assert 0.0 <= y < 20.0


class TestRunDistributed:
    def test_distributed_mode_basic(self):
        """去中心化模式基本收敛。"""
        snapshot = create_snapshot_rectangle(30, 30, 10, 10, 6, 6)
        trajectory = run([snapshot], n_drones=5, seed=42,
                         max_speed=3.0, mode="distributed", comm_radius=20.0, verbose=False)
        assert len(trajectory) == 1
        assert len(trajectory[0]) == 5

    def test_distributed_multi_step(self):
        snapshots = [
            create_snapshot_rectangle(30, 30, 5, 5, 4, 4),
            create_snapshot_rectangle(30, 30, 25, 25, 4, 4),
        ]
        trajectory = run(snapshots, n_drones=8, seed=99,
                         max_speed=float("inf"), mode="distributed", comm_radius=50.0, verbose=False)
        assert len(trajectory) == 2
        for step in trajectory:
            assert len(step) == 8

    def test_distributed_3d(self):
        from src.grid import create_snapshot_sphere
        snapshot = create_snapshot_sphere(20, 20, 10, 10, 10, 5, 4)
        trajectory = run([snapshot], n_drones=4, seed=1,
                         max_speed=float("inf"), mode="distributed", comm_radius=30.0, verbose=False)
        assert len(trajectory) == 1
        # 所有无人机应到达球体内
        snapshot = snapshot
        for x, y, z in trajectory[0]:
            ix, iy, iz = int(round(x)), int(round(y)), int(round(z))
            assert snapshot[iz, iy, ix] is np.True_

    def test_distributed_with_physics(self):
        """分布式 + 物理模式组合不崩溃且收敛。"""
        snapshot = create_snapshot_rectangle(30, 30, 10, 10, 6, 6)
        trajectory = run([snapshot], n_drones=5, seed=42,
                         max_speed=2.0, mode="distributed", comm_radius=20.0,
                         use_physics=True, physics_dt=0.1, max_accel=5.0,
                         verbose=False)
        assert len(trajectory) == 1
        assert len(trajectory[0]) == 5
        for x, y, z in trajectory[0]:
            assert 0.0 <= x < 30.0
            assert 0.0 <= y < 30.0


class TestRunWithPhysics:
    def test_physics_mode_converges(self):
        """use_physics=True 时静态快照最终应收敛到目标。"""
        snapshot = create_snapshot_rectangle(40, 40, 20, 20, 10, 8)
        snapshots = [snapshot] * 3
        trajectory = run(snapshots, n_drones=8, seed=7, max_speed=2.0,
                         use_physics=True, physics_dt=0.1, max_accel=10.0,
                         verbose=False)
        final = trajectory[-1]
        for x, y, z in final:
            ix, iy = int(round(x)), int(round(y))
            assert snapshot[iy, ix] is np.True_

    def test_physics_produces_smooth_trajectory(self):
        """有加速限制时，相邻帧位移不应超过自由落体式位移上限。"""
        snapshot = create_snapshot_rectangle(30, 30, 5, 5, 6, 6)
        snapshots = [
            snapshot,
            create_snapshot_rectangle(30, 30, 25, 25, 6, 6),
        ]
        trajectory = run(snapshots, n_drones=4, seed=99, max_speed=3.0,
                         use_physics=True, physics_dt=0.1, max_accel=10.0,
                         verbose=False)
        assert len(trajectory) == 2
        # 检查相邻时间步的位移：受加速度约束
        for t in range(1, len(trajectory)):
            for i, (p_new, p_old) in enumerate(zip(trajectory[t], trajectory[t - 1])):
                dx = p_new[0] - p_old[0]
                dy = p_new[1] - p_old[1]
                dist = (dx * dx + dy * dy) ** 0.5
                # 位移应有限，不会无限大
                assert dist < 50.0


class TestRunWithCollision:
    def test_collision_avoidance_basic(self):
        """碰撞规避开启不崩溃且收敛。"""
        snapshot = create_snapshot_rectangle(50, 50, 20, 20, 20, 20)
        trajectory = run([snapshot], n_drones=4, seed=42,
                         max_speed=float("inf"), collision_avoidance=True,
                         min_distance=2.0, repulsion_strength=0.5,
                         verbose=False)
        assert len(trajectory) == 1
        for x, y, z in trajectory[0]:
            assert 0.0 <= x < 50.0
            assert 0.0 <= y < 50.0

    def test_collision_with_physics(self):
        """碰撞规避 + 物理模式组合收敛。"""
        snapshot = create_snapshot_rectangle(40, 40, 15, 15, 12, 12)
        snapshots = [snapshot] * 2
        trajectory = run(snapshots, n_drones=6, seed=1, max_speed=2.0,
                         use_physics=True, physics_dt=0.1, max_accel=8.0,
                         collision_avoidance=True, min_distance=1.5,
                         repulsion_strength=0.3, verbose=False)
        assert len(trajectory) == 2
        final = trajectory[-1]
        for x, y, z in final:
            ix, iy = int(round(x)), int(round(y))
            assert snapshot[iy, ix] is np.True_
