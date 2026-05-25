"""
# 1. 功能
碰撞检测与规避模块。检测无人机间距离过近的情况，施加排斥力修正速度。
纯 Python 实现，不依赖 numpy。

# 2. 输入
- drones: Drone 对象列表
- min_distance: 最小安全距离
- strength: 排斥力强度

# 3. 输出
- detect_collisions() → list[tuple[int, int]]: 碰撞对索引
- compute_repulsion() → (fx, fy, fz): 排斥力向量
- avoid_collisions() → int: 碰撞对数

# 4. 核心执行流程
1. 双重循环检测所有无人机对的距离
2. 距离 < min_distance 时计算排斥力: F = strength * (1/d - 1/min) / d^2
3. 力方向从邻居指向自己
4. 直接修改 drone.vx/vy/vz

# 5. 依赖
- math
"""

import math


def detect_collisions(
    drones: list[object],
    min_distance: float,
) -> list[tuple[int, int]]:
    """检测所有距离小于 min_distance 的无人机对。

    Args:
        drones: 有 position 属性的无人机列表
        min_distance: 最小安全距离

    Returns:
        (i, j) 索引对列表，distance < min_distance
    """
    pairs: list[tuple[int, int]] = []
    n = len(drones)
    for i in range(n):
        pi = drones[i].position
        for j in range(i + 1, n):
            pj = drones[j].position
            dx = pi[0] - pj[0]
            dy = pi[1] - pj[1]
            dz = pi[2] - pj[2] if len(pi) > 2 and len(pj) > 2 else 0.0
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            if dist < min_distance:
                pairs.append((i, j))
    return pairs


def compute_repulsion(
    drone: object,
    neighbor: object,
    min_distance: float,
    strength: float,
) -> tuple[float, float, float]:
    """计算 neighbor 对 drone 的排斥力向量。

    Args:
        drone: 被推开的无人机（有 position 属性）
        neighbor: 排斥源无人机（有 position 属性）
        min_distance: 最小安全距离
        strength: 排斥力强度

    Returns:
        (fx, fy, fz) 排斥力
    """
    px, py, pz = drone.position
    nx, ny, nz = neighbor.position
    dx = px - nx
    dy = py - ny
    dz = pz - nz
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)

    if dist < 1e-9 or dist >= min_distance:
        return (0.0, 0.0, 0.0)

    # F = strength * (1/d - 1/min) / d^2，方向从 neighbor 指向 drone
    mag = strength * (1.0 / dist - 1.0 / min_distance) / (dist * dist)
    return (dx * mag, dy * mag, dz * mag)


def avoid_collisions(
    drones: list[object],
    min_distance: float = 1.0,
    strength: float = 1.0,
) -> int:
    """检测碰撞对并施加排斥力到 drone.vx/vy/vz。

    Args:
        drones: Drone 对象列表
        min_distance: 最小安全距离
        strength: 排斥力强度

    Returns:
        碰撞对数量
    """
    pairs = detect_collisions(drones, min_distance)
    for i, j in pairs:
        fx, fy, fz = compute_repulsion(drones[i], drones[j], min_distance, strength)
        drones[i].vx += fx
        drones[i].vy += fy
        drones[i].vz += fz
        # 对 j 施加反向力
        drones[j].vx -= fx
        drones[j].vy -= fy
        drones[j].vz -= fz
    return len(pairs)
