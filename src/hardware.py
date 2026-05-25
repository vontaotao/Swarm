"""
# 1. 功能
硬件抽象接口层。定义 HardwareInterface 抽象基类，为未来 MAVLink/ROS
等真实硬件接入预留接口。当前提供 SimulatedDrone 实现。

# 2. 输入
- HardwareInterface: 抽象基类，定义统一接口
- SimulatedDrone: 包装 Drone 对象，无 physics 时用 move_toward，有 physics 时用 physics_step

# 3. 输出
- get_position() → (x, y, z)
- get_velocity() → (vx, vy, vz)
- send_target(tx, ty, tz) → None
- update(dt) → bool（是否已到达）

# 4. 核心执行流程
- SimulatedDrone.send_target() 记录目标
- SimulatedDrone.update(dt) 根据是否有 PhysicsConfig 选择 physics_step 或 move_toward

# 5. 依赖
- abc, src.drone, src.physics
"""

from abc import ABC, abstractmethod

from src.drone import Drone
from src.physics import PhysicsConfig, physics_step


class HardwareInterface(ABC):
    """无人机硬件抽象接口。未来 MAVLink/ROS 等实现只需实现此接口。"""

    @abstractmethod
    def get_position(self) -> tuple[float, float, float]:
        """返回当前位置 (x, y, z)。"""
        ...

    @abstractmethod
    def get_velocity(self) -> tuple[float, float, float]:
        """返回当前速度 (vx, vy, vz)。"""
        ...

    @abstractmethod
    def send_target(self, tx: float, ty: float, tz: float = 0.0) -> None:
        """发送目标位置指令。"""
        ...

    @abstractmethod
    def update(self, dt: float) -> bool:
        """推进一步物理/运动学更新。返回 True 表示已到达目标。"""
        ...


class SimulatedDrone(HardwareInterface):
    """基于 Drone 模型的仿真实现。无 physics 时用运动学，有 physics 时用动力学。"""

    def __init__(self, drone: Drone, physics: PhysicsConfig | None = None):
        self._drone = drone
        self._physics = physics
        self._target: tuple[float, float, float] | None = None

    def get_position(self) -> tuple[float, float, float]:
        return self._drone.position

    def get_velocity(self) -> tuple[float, float, float]:
        return self._drone.velocity

    def send_target(self, tx: float, ty: float, tz: float = 0.0) -> None:
        self._target = (float(tx), float(ty), float(tz))

    def update(self, dt: float) -> bool:
        """推进一步。无目标时返回 True（视为已到达）。"""
        if self._target is None:
            return True
        tx, ty, tz = self._target
        if self._physics is not None:
            cfg = PhysicsConfig(
                dt=dt,
                max_accel=self._physics.max_accel,
                drag=self._physics.drag,
                mass=self._physics.mass,
            )
            return physics_step(self._drone, tx, ty, tz, cfg)
        else:
            self._drone.set_target(tx, ty, tz)
            return self._drone.move_toward(tx, ty, tz)

    def __repr__(self) -> str:
        mode = "physics" if self._physics else "kinematic"
        return f"SimulatedDrone({self._drone}, mode={mode})"
