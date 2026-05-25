# 项目总计划 — Swarm 无人机群空间快照补位系统

## 项目目标

构建一个无人机群控制的仿真系统。中央电脑在每个时间步发布"空间快照"（目标编队的空间分布），无人机群基于最近邻原则自动补位形成编队。

## 里程碑

### 里程碑 1: 核心仿真引擎（已完成）

- 目标：实现"空间快照 + 最近邻补位"最小闭环
- 范围：2D 网格、静态快照图案、瞬时移动、命令行输出
- 模块：grid / drone / matcher / simulation + 单元测试
- 详见 `goals/001-core-simulation.md`

### 里程碑 2: 动态快照 + 基础可视化（已完成）

- [x] 快照序列化（随时间变化）— `src/choreographer.py`
- [x] 使用 matplotlib 生成 GIF 动画 — `src/visualizer.py`
- [x] 无人机运动学约束（速度上限）— `drone.move_toward()` + 内层收敛循环

### 里程碑 3: 三维扩展 + 通信模型 + 去中心化（已完成）

- [x] 3D 空间仿真 — drone/matcher/grid 维度通用化
- [x] 无人机间点对点通信 — `src/comm.py`
- [x] 分布式/"无中央协调"变体 — `src/distributed_matcher.py`

### 里程碑 4: 轻量动力学 + 碰撞检测 + 硬件抽象（已完成）

- [x] 轻量动力学引擎 — `src/physics.py`（纯 Python 欧拉积分，加速度/阻力/质量）
- [x] 硬件抽象接口 — `src/hardware.py`（HardwareInterface ABC + SimulatedDrone）
- [x] 碰撞检测与规避 — `src/collision.py`（排斥力模型）
- [x] 仿真循环和去中心化匹配均支持物理 + 碰撞参数
- [x] 零外部依赖，全部新参数有默认值
- 详见 `goals/004-physics-hardware.md`

### 里程碑 5: 待规划
