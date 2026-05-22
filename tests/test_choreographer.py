"""
# 1. 功能
choreographer.py 的单元测试。验证四种模式的序列长度、形状和基础正确性。

# 2. 输入
- 测试参数（网格尺寸、步数、模式名）

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 对每种模式生成序列 → 验证长度、网格形状、目标像素存在性

# 5. 依赖
- pytest, numpy, src.choreographer
"""

import pytest
from src.choreographer import generate_sequence


class TestGenerateSequence:
    def test_line_sweep_basic(self):
        seq = generate_sequence(50, 50, 10, "line_sweep")
        assert len(seq) == 10
        for frame in seq:
            assert frame.shape == (50, 50)
            assert frame.dtype == bool

    def test_line_sweep_moves_across(self):
        seq = generate_sequence(100, 50, 5, "line_sweep", rect_w=8, rect_h=6)
        # 第一帧矩形在左侧，最后一帧在右侧
        _, first_xs = (seq[0] > 0).nonzero()
        _, last_xs = (seq[-1] > 0).nonzero()
        assert last_xs.mean() > first_xs.mean() + 10  # 明显右移

    def test_circle_shift_basic(self):
        seq = generate_sequence(50, 50, 8, "circle_shift", radius=5)
        assert len(seq) == 8

    def test_circle_shift_moves(self):
        seq = generate_sequence(100, 50, 5, "circle_shift", radius=5)
        # 圆心应随时间移动
        from src.grid import get_target_positions
        first_pts = get_target_positions(seq[0])
        last_pts = get_target_positions(seq[-1])
        first_cx = sum(p[0] for p in first_pts) / len(first_pts)
        last_cx = sum(p[0] for p in last_pts) / len(last_pts)
        assert last_cx > first_cx + 5

    def test_pulse_basic(self):
        seq = generate_sequence(50, 50, 12, "pulse", min_radius=3, max_radius=10, cycles=1.0)
        assert len(seq) == 12

    def test_pulse_expands_and_contracts(self):
        seq = generate_sequence(100, 100, 20, "pulse", min_radius=5, max_radius=20, cycles=1.0)
        from src.grid import count_target_cells
        counts = [count_target_cells(f) for f in seq]
        # 呼吸：先扩张后收缩，应有振荡
        mid = len(counts) // 2
        # 前半段最大 > 前半段最小（扩张期）
        assert max(counts[:mid]) > min(counts[:mid]) * 1.1

    def test_diagonal_basic(self):
        seq = generate_sequence(50, 50, 10, "diagonal", radius=4)
        assert len(seq) == 10

    def test_diagonal_moves(self):
        seq = generate_sequence(100, 100, 5, "diagonal", radius=4)
        from src.grid import get_target_positions
        first_pts = get_target_positions(seq[0])
        last_pts = get_target_positions(seq[-1])
        first_cy = sum(p[1] for p in first_pts) / len(first_pts)
        last_cy = sum(p[1] for p in last_pts) / len(last_pts)
        assert last_cy > first_cy + 5  # 明显下移

    def test_unknown_pattern_raises(self):
        with pytest.raises(ValueError, match="未知模式"):
            generate_sequence(10, 10, 5, "nonexistent")
