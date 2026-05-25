# Swarm — 无人机群空间快照补位仿真

中央电脑每个时间步发布"空间快照"（目标编队的空间分布），无人机群基于 **最近邻原则** 自动就近补位，形成目标编队。支持 2D/3D、集中式/去中心化两种匹配模式，可选轻量动力学引擎和碰撞规避。

## 核心算法

```
t 时刻集中式:
  1. 在位检测 — 无人机当前位置是否已在目标像素上
  2. 空缺收集 — 收集所有未被填充的目标像素
  3. 距离优先贪心分配 — 按最近空缺距离升序排列，依次匹配
  4. 收敛 → 推进到 t+1

t 时刻去中心化:
  1. 在位检测 → 广播 CLAIM
  2. 收集已声明空缺，未分配无人机找最近未声明空缺
  3. 广播 CLAIM + 冲突解决（距离近者胜）
  4. 渐进移动 → 收敛 → 推进到 t+1
```

## 项目结构

```
src/
├── grid.py                # 空间网格 + 编队图案 (2D/3D)
├── drone.py               # 无人机个体 (位置/速度/加速度/质量)
├── matcher.py             # 集中式匹配（核心，维度自适应）
├── simulation.py          # 主仿真循环（支持双模式 + 物理 + 碰撞）
├── choreographer.py       # 动态快照序列生成器 (6种模式)
├── visualizer.py          # matplotlib GIF 渲染 (2D/3D切片)
├── comm.py                # 无人机通信网络
├── distributed_matcher.py # 去中心化匹配算法
├── physics.py             # 轻量动力学引擎（欧拉积分）
├── collision.py           # 碰撞检测与规避
└── hardware.py            # 硬件抽象接口（MAVLink/ROS 预留）
tests/                     # 124 项单元测试
docs/planning/             # 项目规划文档
```

## 快速开始

```bash
pip install numpy pytest matplotlib
python -m pytest tests/ -v   # 124 项测试
```

```python
# 2D 集中式仿真 + GIF
from src.choreographer import generate_sequence
from src.simulation import run
from src.visualizer import render_gif

seq = generate_sequence(60, 60, 25, 'circle_shift', radius=6)
traj = run(seq, n_drones=12, max_speed=2.5, seed=42)
render_gif(traj, seq, 'swarm.gif', fps=6)
```

```python
# 3D 去中心化仿真 + GIF
from src.grid import create_snapshot_sphere

seq = [create_snapshot_sphere(30, 40, 15, 10+i*2, 20, 8, 6) for i in range(20)]
traj = run(seq, n_drones=25, max_speed=2.0, mode='distributed', comm_radius=20.0)
render_gif(traj, seq, 'swarm3d.gif', fps=6, slice_z=8)
```

```python
# 物理模式 + 碰撞规避 + GIF
from src.choreographer import generate_sequence

seq = generate_sequence(60, 60, 30, 'circle_shift', radius=6)
traj = run(seq, n_drones=15, max_speed=2.5, seed=42,
           use_physics=True, physics_dt=0.1, max_accel=5.0,
           collision_avoidance=True, min_distance=1.5)
render_gif(traj, seq, 'swarm_physics.gif', fps=8)
```

## 进度

- [x] 里程碑 1：核心仿真引擎（grid / drone / matcher / simulation）
- [x] 里程碑 2：动态快照序列 + matplotlib 可视化 + 速度约束
- [x] 里程碑 3：3D 扩展 + 通信模型 + 去中心化
- [x] 里程碑 4：轻量动力学 + 碰撞检测 + 硬件抽象接口
- [ ] 里程碑 5：待规划

详见 `docs/planning/PROJECT_STATUS.md`

## 许可

MIT — 见 [LICENSE](LICENSE)
