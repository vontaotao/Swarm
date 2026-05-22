"""
# 1. 功能
无人机个体模块。定义单架无人机的状态（ID、三维位置）和基本行为（距离计算、移动）。
2D 场景 z 默认为 0，不影响现有调用。

# 2. 输入
- drone_id: 无人机唯一标识
- x, y, z: 初始坐标（z 默认 0.0）
- max_speed: 每时间步最大移动距离（默认 inf = 无限制）

# 3. 输出
- 自身状态信息，position 始终返回 (x, y, z) 三元组

# 4. 核心执行流程
- 初始化时记录 ID、三维位置、速度上限
- distance_to(tx, ty, tz): 计算欧几里得距离
- move_to(tx, ty, tz): 瞬时移动
- move_toward(tx, ty, tz): 向目标移动一步，受 max_speed 约束

# 5. 依赖
- math
"""

import math


class Drone:
    """单架无人机，支持 2D/3D 空间。"""

    def __init__(self, drone_id: int, x: float, y: float, z: float = 0.0, max_speed: float = float("inf")):
        self.id = drone_id
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.max_speed = float(max_speed)

    @property
    def position(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def distance_to(self, tx: float, ty: float, tz: float = 0.0) -> float:
        """计算当前位置到目标点 (tx, ty, tz) 的欧几里得距离。"""
        dx = self.x - tx
        dy = self.y - ty
        dz = self.z - tz
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def move_to(self, tx: float, ty: float, tz: float = 0.0) -> None:
        """瞬间移动到目标位置 (tx, ty, tz)。"""
        self.x = float(tx)
        self.y = float(ty)
        self.z = float(tz)

    def move_toward(self, tx: float, ty: float, tz: float = 0.0) -> bool:
        """向目标移动一步，受 max_speed 约束。

        Returns:
            True 表示已到达目标，False 表示还在移动中。
        """
        dx = tx - self.x
        dy = ty - self.y
        dz = tz - self.z
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist <= self.max_speed or dist < 1e-9:
            self.x = float(tx)
            self.y = float(ty)
            self.z = float(tz)
            return True
        frac = self.max_speed / dist
        self.x += dx * frac
        self.y += dy * frac
        self.z += dz * frac
        return False

    def __repr__(self) -> str:
        return f"Drone(id={self.id}, pos=({self.x:.1f}, {self.y:.1f}, {self.z:.1f}))"
