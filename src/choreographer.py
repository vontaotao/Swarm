"""
# 1. 功能
动态快照序列生成器（编舞器）。将静态图案组合成随时间变化的快照序列，
支持平移、缩放等运动模式。

# 2. 输入
- 网格尺寸 (width, height)、步数 n_steps、模式名称 pattern
- 模式相关参数（起点/终点、半径等）

# 3. 输出
- list[np.ndarray]: 长度为 n_steps 的快照序列，每个形状为 (height, width) 的布尔矩阵

# 4. 核心执行流程
- 根据 pattern 名称分发到对应的序列生成函数
- 每帧计算插值后的几何参数（中心、半径）
- 调用 grid.py 的 create_snapshot_* 生成单帧

# 5. 依赖
- numpy, src.grid
"""

import numpy as np
from src.grid import (
    create_snapshot_rectangle,
    create_snapshot_circle,
    create_snapshot_hollow_circle,
)


def _lerp(a: float, b: float, t: float) -> float:
    """线性插值。"""
    return a + (b - a) * t


def _lerp_int(a: int, b: int, t: float) -> int:
    """整数线性插值（四舍五入）。"""
    return int(round(a + (b - a) * t))


def _sequence_line_sweep(
    width: int, height: int, n_steps: int, rect_w: int = 8, rect_h: int = 6
) -> list[np.ndarray]:
    """矩形编队从左到右平移扫过网格。"""
    seq = []
    y = height // 2
    x0 = rect_w // 2
    x1 = width - rect_w // 2 - 1
    for t in range(n_steps):
        frac = t / max(n_steps - 1, 1)
        cx = _lerp_int(x0, x1, frac)
        seq.append(create_snapshot_rectangle(width, height, cx, y, rect_w, rect_h))
    return seq


def _sequence_circle_shift(
    width: int, height: int, n_steps: int,
    start: tuple[int, int] = None, end: tuple[int, int] = None,
    radius: int = 6
) -> list[np.ndarray]:
    """圆形编队从 start 平移到 end。"""
    if start is None:
        start = (radius + 2, height // 2)
    if end is None:
        end = (width - radius - 2, height // 2)
    seq = []
    for t in range(n_steps):
        frac = t / max(n_steps - 1, 1)
        cx = _lerp_int(start[0], end[0], frac)
        cy = _lerp_int(start[1], end[1], frac)
        seq.append(create_snapshot_circle(width, height, cx, cy, radius))
    return seq


def _sequence_pulse(
    width: int, height: int, n_steps: int,
    cx: int = None, cy: int = None,
    min_radius: int = 4, max_radius: int = 15, cycles: float = 1.0
) -> list[np.ndarray]:
    """圆环呼吸般缩放——内半径 sin 振荡，外半径跟随。"""
    if cx is None:
        cx = width // 2
    if cy is None:
        cy = height // 2
    seq = []
    for t in range(n_steps):
        frac = t / max(n_steps - 1, 1)
        phase = frac * 2.0 * np.pi * cycles
        # sin 振荡：在 min 和 max 之间
        mid = (min_radius + max_radius) / 2.0
        amp = (max_radius - min_radius) / 2.0
        outer = int(round(mid + amp * np.sin(phase)))
        inner = max(0, outer - 3)
        seq.append(create_snapshot_hollow_circle(width, height, cx, cy, inner, outer))
    return seq


def _sequence_diagonal(
    width: int, height: int, n_steps: int, radius: int = 5
) -> list[np.ndarray]:
    """圆形编队从左上角移动到右下角。"""
    seq = []
    margin = radius + 2
    for t in range(n_steps):
        frac = t / max(n_steps - 1, 1)
        cx = _lerp_int(margin, width - margin - 1, frac)
        cy = _lerp_int(margin, height - margin - 1, frac)
        seq.append(create_snapshot_circle(width, height, cx, cy, radius))
    return seq


# 模式注册表
_PATTERNS = {
    "line_sweep": _sequence_line_sweep,
    "circle_shift": _sequence_circle_shift,
    "pulse": _sequence_pulse,
    "diagonal": _sequence_diagonal,
}


def generate_sequence(
    width: int,
    height: int,
    n_steps: int,
    pattern: str = "circle_shift",
    **kwargs,
) -> list[np.ndarray]:
    """生成动态快照序列。

    Args:
        width: 网格宽度
        height: 网格高度
        n_steps: 序列长度（帧数）
        pattern: 模式名称，可选 "line_sweep", "circle_shift", "pulse", "diagonal"
        **kwargs: 传给具体模式的参数（如 radius, cycles 等）

    Returns:
        长度为 n_steps 的快照列表
    """
    if pattern not in _PATTERNS:
        raise ValueError(
            f"未知模式: {pattern}，可选: {list(_PATTERNS.keys())}"
        )
    return _PATTERNS[pattern](width, height, n_steps, **kwargs)
