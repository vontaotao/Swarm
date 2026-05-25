# 项目当前状态

## 当前阶段

**里程碑 4: 轻量动力学 + 碰撞检测 + 硬件抽象** — 已实现。

## 已完成

### 里程碑 1: 核心仿真引擎
- [x] grid / drone / matcher / simulation + 测试

### 里程碑 2: 动态快照 + 基础可视化
- [x] choreographer.py / visualizer.py + 速度约束 + 内层收敛

### 里程碑 3: 三维扩展 + 通信模型 + 去中心化
- [x] `src/drone.py` — 位置改为 (x, y, z) 三元组，所有方法支持 z 轴
- [x] `src/matcher.py` — 维度通用化（_sq_dist + 可变长元组处理），2D/3D 自动适配
- [x] `src/grid.py` — 新增 create_snapshot_box / create_snapshot_sphere (3D)
- [x] `src/comm.py` — 通信网络模块（消息广播/接收，通信半径限制）
- [x] `src/distributed_matcher.py` — 去中心化匹配（声明 + 冲突解决 + 收敛）
- [x] `src/simulation.py` — 新增 mode="distributed" + comm_radius 参数
- [x] `src/choreographer.py` — 新增 sphere_shift / sphere_pulse 3D 模式
- [x] `src/visualizer.py` — 3D 切片投影渲染（slice_z 参数）
- [x] 全部 83 项测试通过

### 里程碑 4: 轻量动力学 + 碰撞检测 + 硬件抽象
- [x] `src/drone.py` — 新增 vx/vy/vz 速度状态、max_accel/drag/mass 物理参数、set_target()
- [x] `src/physics.py` — 轻量动力学引擎（PhysicsConfig + physics_step，纯 Python 欧拉积分）
- [x] `src/hardware.py` — 硬件抽象接口（HardwareInterface ABC + SimulatedDrone）
- [x] `src/collision.py` — 碰撞检测与规避（detect + repulsion + avoid）
- [x] `src/simulation.py` — 新增 use_physics / collision_avoidance 等参数
- [x] `src/distributed_matcher.py` — 支持物理模式和碰撞规避
- [x] 全部 124 项测试通过

## 下一步

- 里程碑 5：待规划
- 当前可执行 `python -m pytest tests/ -v` 验证全部测试（124 项）
- 物理模式端到端示例：
  ```python
  from src.choreographer import generate_sequence
  from src.simulation import run
  from src.visualizer import render_gif

  seq = generate_sequence(60, 60, 30, 'circle_shift', radius=6)
  traj = run(seq, n_drones=15, max_speed=2.5, seed=42,
             use_physics=True, physics_dt=0.1, max_accel=5.0,
             collision_avoidance=True, min_distance=1.5)
  render_gif(traj, seq, 'swarm_physics.gif', fps=8)
  ```

## 风险

（暂无）
