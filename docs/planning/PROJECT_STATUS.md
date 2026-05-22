# 项目当前状态

## 当前阶段

**里程碑 3: 三维扩展 + 通信模型 + 去中心化** — 已实现。

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

## 下一步

- 里程碑 4 规划：硬件接口（MAVLink / ROS）
- 当前可执行 `python -m pytest tests/ -v` 验证全部测试
- 3D 端到端示例：
  ```python
  from src.grid import create_snapshot_sphere
  from src.simulation import run
  from src.visualizer import render_gif
  seq = [create_snapshot_sphere(30, 40, 15, 10+i*2, 20, 8, 6) for i in range(20)]
  traj = run(seq, n_drones=25, max_speed=2.0, mode='distributed', comm_radius=20.0)
  render_gif(traj, seq, 'swarm3d.gif', fps=6, slice_z=8)
  ```

## 风险

（暂无）
