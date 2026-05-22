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
            for x, y in step:
                # 位置应在网格范围内
                assert 0.0 <= x < 30.0
                assert 0.0 <= y < 30.0

    def test_all_drones_reach_targets(self):
        """当目标像素足够多时，所有无人机都应到达目标位置。"""
        snapshot = create_snapshot_rectangle(50, 50, 25, 25, 20, 20)  # 400 个目标
        snapshots = [snapshot] * 3  # 静态快照，多次迭代
        trajectory = run(snapshots, n_drones=30, seed=0, verbose=False)
        # 第一步后所有 30 架都应就位（400 > 30）
        final = trajectory[-1]
        for x, y in final:
            ix, iy = int(round(x)), int(round(y))
            assert snapshot[iy, ix] is np.True_
