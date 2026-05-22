"""
# 1. 功能
无人机个体模块。定义单架无人机的状态（ID、位置）和基本行为（距离计算、移动）。

# 2. 输入
- drone_id: 无人机唯一标识
- position: (x, y) 初始坐标
- max_speed: 每时间步最大移动距离（默认 inf = 无限制）

# 3. 输出
- 自身状态信息，move_to() / move_toward() 后更新位置

# 4. 核心执行流程
- 初始化时记录 ID 和初始位置、速度上限
- distance_to(target): 计算到目标点的欧几里得距离
- move_to(target): 瞬时移动到目标位置
- move_toward(target): 向目标移动一步，受 max_speed 约束

# 5. 依赖
- math
"""

import math


class Drone:
    """单架无人机。"""

    def __init__(self, drone_id: int, x: float, y: float, max_speed: float = float("inf")):
        self.id = drone_id
        self.x = float(x)
        self.y = float(y)
        self.max_speed = float(max_speed)

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

    def move_toward(self, tx: float, ty: float) -> bool:
        """向目标移动一步，受 max_speed 约束。

        Returns:
            True 表示已到达目标，False 表示还在移动中。
        """
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= self.max_speed or dist < 1e-9:
            self.x = float(tx)
            self.y = float(ty)
            return True
        # 按比例移动 max_speed 距离
        frac = self.max_speed / dist
        self.x += dx * frac
        self.y += dy * frac
        return False

    def __repr__(self) -> str:
        return f"Drone(id={self.id}, pos=({self.x:.1f}, {self.y:.1f}))"
