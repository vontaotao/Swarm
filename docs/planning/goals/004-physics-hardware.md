# 目标 004: 轻量动力学 + 碰撞检测 + 硬件抽象接口

## 状态

已完成 (2026-05-25)

## 目标描述

在现有运动学仿真之上加入：轻量动力学模型、无人机间碰撞检测与规避、硬件抽象接口层。

## 验收标准

- [x] drone.py 新增 vx/vy/vz 速度属性、max_accel/drag/mass 物理参数、set_target()
- [x] physics.py PhysicsConfig + physics_step() 纯 Python 欧拉积分
- [x] hardware.py HardwareInterface ABC + SimulatedDrone 包装实现
- [x] collision.py detect_collisions + compute_repulsion + avoid_collisions
- [x] simulation.py run() 新增 use_physics / collision_avoidance 等参数
- [x] distributed_matcher.py 支持物理模式和碰撞规避分支
- [x] 全部 124 项测试通过，无回归

## 技术决策

- **零外部依赖**：动力学和碰撞均纯 Python + math，不引入新 pip 包
- **move_toward 不变**：物理模式通过独立的 physics_step 函数提供，保持向后兼容
- **碰撞 = 战术层**：碰撞规避在匹配决策之后微调速度，不与匹配算法耦合
- **接口优先**：HardwareInterface ABC 为未来 MAVLink/ROS 预留插槽
- **所有新参数有默认值**：use_physics=False, collision_avoidance=False，默认行为不变

## 测试结果

```
124 passed in 1.00s
```

## 新增文件

| 文件 | 测试数 |
|------|--------|
| src/physics.py | test_physics.py (11) |
| src/hardware.py | test_hardware.py (9) |
| src/collision.py | test_collision.py (11) |
| src/drone.py (追加) | test_drone.py (5 new) |
| src/simulation.py (追加) | test_simulation.py (5 new) |
