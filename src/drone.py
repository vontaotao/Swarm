"""
# 1. 功能
无人机个体模块。定义单架无人机的状态（ID、位置）和基本行为（距离计算、移动）。

# 2. 输入
- drone_id: 无人机唯一标识
- position: (x, y) 初始坐标

# 3. 输出
- 自身状态信息，move_to() 后返回新位置

# 4. 核心执行流程
- 初始化时记录 ID 和初始位置
- distance_to(target): 计算到目标点的欧几里得距离
- move_to(target): 瞬时移动到目标位置，返回自身

# 5. 依赖
- math
"""

import math


class Drone:
    """单架无人机。"""

    def __init__(self, drone_id: int, x: float, y: float):
        self.id = drone_id
        self.x = float(x)
        self.y = float(y)

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    def distance_to(self, tx: float, ty: float) -> float:
        """计算当前位置到目标点 (tx, ty) 的欧几里得距离。"""
        return math.sqrt((self.x - tx) ** 2 + (self.y - ty) ** 2)

    def move_to(self, tx: float, ty: float) -> None:
        """瞬间移动到目标位置 (tx, ty)。"""
        self.x = float(tx)
        self.y = float(ty)

    def __repr__(self) -> str:
        return f"Drone(id={self.id}, pos=({self.x:.1f}, {self.y:.1f}))"
