"""
# 1. 功能
轻量动力学引擎。用欧拉积分替代纯运动学线性插值，提供速度/加速度/阻力约束。
不引入外部依赖，纯 Python + math 实现。

# 2. 输入
- drone: Drone 对象（需有 position, velocity, max_speed, max_accel, drag, mass 属性）
- tx, ty, tz: 目标坐标
- config: PhysicsConfig（dt, max_accel, drag, mass 超控 drone 默认值）

# 3. 输出
- bool: True 表示已到达目标（位置 + 速度均接近零），False 表示仍在移动中

# 4. 核心执行流程
1. 计算目标方向单位向量
2. 期望速度 = dir * min(max_speed, |dir|/dt)
3. 所需加速度 clamp 到 [-max_accel, max_accel]
4. 施加阻力 a -= drag * v
5. 欧拉积分: v += a*dt, pos += v*dt
6. 到达判定: |pos-target| < 1e-6 且 |v| < 1e-6

# 5. 依赖
- math, dataclasses
"""

import math
from dataclasses import dataclass


@dataclass
class PhysicsConfig:
    """动力学参数配置。所有参数有默认值，不传时无物理约束。"""

    max_accel: float = float("inf")
    drag: float = 0.0
    mass: float = 1.0
    dt: float = 0.1


def physics_step(drone: object, tx: float, ty: float, tz: float,
                 config: PhysicsConfig) -> bool:
    """单步欧拉积分，向目标移动。返回是否到达目标。

    直接修改 drone 的 x/y/z 和 vx/vy/vz 属性。
    使用 config 中的参数，物理参数优先用 drone 自身值（若不为默认值）。
    """
    mass = drone.mass if drone.mass != 1.0 else config.mass
    max_accel = drone.max_accel if drone.max_accel != float("inf") else config.max_accel
    drag = drone.drag if drone.drag != 0.0 else config.drag
    dt = config.dt

    px, py, pz = drone.position
    dx = tx - px
    dy = ty - py
    dz = tz - pz
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)

    # 到达判定
    speed = math.sqrt(drone.vx * drone.vx + drone.vy * drone.vy + drone.vz * drone.vz)
    if dist < 1e-6 and speed < 1e-6:
        drone.x = float(tx)
        drone.y = float(ty)
        drone.z = float(tz)
        drone.vx = 0.0
        drone.vy = 0.0
        drone.vz = 0.0
        return True

    if dist < 1e-9:
        drone.vx = 0.0
        drone.vy = 0.0
        drone.vz = 0.0
        return True

    # 无约束时直接跳跃（保持与 move_toward 一致的瞬时行为）
    if drone.max_speed == float("inf") and max_accel == float("inf"):
        drone.x = float(tx)
        drone.y = float(ty)
        drone.z = float(tz)
        drone.vx = 0.0
        drone.vy = 0.0
        drone.vz = 0.0
        return True

    # 方向单位向量
    inv_dist = 1.0 / dist
    dir_x = dx * inv_dist
    dir_y = dy * inv_dist
    dir_z = dz * inv_dist

    # 期望速度: 不超过 max_speed，也不超过 dist/dt
    max_v = min(drone.max_speed, dist / dt)
    desired_vx = dir_x * max_v
    desired_vy = dir_y * max_v
    desired_vz = dir_z * max_v

    # 所需加速度
    ax = (desired_vx - drone.vx) / dt
    ay = (desired_vy - drone.vy) / dt
    az = (desired_vz - drone.vz) / dt

    # 施加阻力
    ax -= drag * drone.vx
    ay -= drag * drone.vy
    az -= drag * drone.vz

    # 加速度 clamp
    if max_accel != float("inf"):
        a_mag = math.sqrt(ax * ax + ay * ay + az * az)
        if a_mag > max_accel:
            a_scale = max_accel / a_mag
            ax *= a_scale
            ay *= a_scale
            az *= a_scale

    # 质量影响
    ax /= mass
    ay /= mass
    az /= mass

    # 欧拉积分
    drone.vx += ax * dt
    drone.vy += ay * dt
    drone.vz += az * dt

    drone.x += drone.vx * dt
    drone.y += drone.vy * dt
    drone.z += drone.vz * dt

    return False
