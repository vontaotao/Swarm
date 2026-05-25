<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-139_passed-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/deps-numpy_%7C_matplotlib-6c5ce7?style=flat-square" alt="Deps">
  <img src="https://img.shields.io/badge/dimensions-2D_%2F_3D-00b894?style=flat-square" alt="2D/3D">
  <img src="https://img.shields.io/badge/mode-centralized_%7C_distributed-0984e3?style=flat-square" alt="Mode">
  <img src="https://img.shields.io/badge/physics-euler_integration-e17055?style=flat-square" alt="Physics">
</p>

<h1 align="center">Swarm</h1>

<p align="center">
  <em>drone swarm · snapshot-based formation filling · nearest-neighbor matching</em>
  <br/>
  <em>无人机群 · 空间快照补位 · 最近邻匹配</em>
</p>

---

**Swarm** is a simulation system for drone swarm formation control. At each timestep, a central computer publishes a *spatial snapshot* — a boolean grid encoding the desired formation — and drones autonomously fill the nearest unoccupied target cells following a greedy nearest-neighbor rule.

**Swarm** 是一个无人机群编队控制仿真系统。中央电脑在每个时间步发布"空间快照"（目标编队的空间分布），无人机群基于最近邻原则自动补位，形成目标编队。

---

## Table of Contents / 目录

- [Features / 特性](#features--特性)
- [Installation / 安装](#installation--安装)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [Examples / 示例](#examples--示例)
- [Architecture / 架构](#architecture--架构)
- [Documentation / 文档](#documentation--文档)
- [License / 许可](#license--许可)

---

## Features / 特性

|        |                                                                                |
| :----- | :----------------------------------------------------------------------------- |
| 🌐     | **2D & 3D** — dimension-agnostic engine, same API for both                     |
| 🧠     | **Dual mode** — centralized global matching & decentralized consensus via P2P comm |
| ⚡     | **Physics engine** — acceleration, drag, mass constraints with Euler integration |
| 🛡️     | **Collision avoidance** — repulsion-force model, decoupled from matching logic  |
| 🎬     | **6 built-in formations** — rectangle, circle, hollow ring, box, sphere, custom points |
| 📹     | **GIF visualization** — matplotlib-based, Z-slice projection for 3D             |
| 🔌     | **Hardware abstraction** — `HardwareInterface` ABC ready for MAVLink / ROS       |
| 📦     | **Zero new deps** — physics & collision in pure Python + math                    |

---

## Installation / 安装

```bash
git clone https://github.com/vontaotao/Swarm.git
cd Swarm
pip install numpy pytest matplotlib
```

Run the test suite / 运行测试：

```bash
python -m pytest tests/ -v
# 139 passed ✅
```

---

## Quick Start / 快速开始

```python
from src.choreographer import generate_sequence
from src.simulation import run
from src.visualizer import render_gif

# 2D centralized: a circle formation glides across the grid
# 2D 集中式：圆形编队水平移动
seq = generate_sequence(60, 60, 25, 'circle_shift', radius=6)
traj = run(seq, n_drones=12, max_speed=2.5, seed=42)
render_gif(traj, seq, 'swarm.gif', fps=6)
```

---

## Examples / 示例

### 3D Decentralized / 3D 去中心化

Drones negotiate via P2P communication — no central matcher.

无人机通过点对点通信协商补位，无中央协调器。

```python
from src.grid import create_snapshot_sphere

seq = [create_snapshot_sphere(30, 40, 15, 10 + i * 2, 20, 8, 6) for i in range(20)]
traj = run(seq, n_drones=25, max_speed=2.0, mode='distributed', comm_radius=20.0)
render_gif(traj, seq, 'swarm3d.gif', fps=6, slice_z=8)
```

### Physics Mode + Collision Avoidance / 物理模式 + 碰撞规避

Realistic drone dynamics with acceleration limits and in-flight collision prevention.

真实动力学约束与飞行中碰撞预防。

```python
seq = generate_sequence(60, 60, 30, 'circle_shift', radius=6)
traj = run(seq, n_drones=15, max_speed=2.5, seed=42,
           use_physics=True, physics_dt=0.1, max_accel=5.0,
           collision_avoidance=True, min_distance=1.5)
render_gif(traj, seq, 'swarm_physics.gif', fps=8)
```

---

## Architecture / 架构

```
src/
├── grid.py                 Spatial grid + formation primitives (2D/3D)
├── drone.py                Individual drone (position, velocity, physics params)
├── matcher.py              Centralized nearest-neighbor greedy matching
├── simulation.py           Main sim loop (supports dual mode + physics + collision)
├── choreographer.py        Dynamic snapshot sequence generator (6 patterns)
├── visualizer.py           matplotlib GIF renderer (2D / 3D Z-slice projection)
├── comm.py                 Peer-to-peer communication network (radius-limited)
├── distributed_matcher.py  Decentralized CLAIM-based negotiation protocol
├── physics.py              Lightweight Euler-integration dynamics engine
├── collision.py            Collision detection & repulsion-force avoidance
└── hardware.py             HardwareInterface ABC (MAVLink / ROS placeholder)

tests/                      139 unit tests
docs/                       Algorithm docs & project planning
```

### Simulation Pipeline / 仿真流水线

```
Snapshot(t) → Match(t) → Move(drones) → CollisionAvoid → Trajectory(t) → Snapshot(t+1)
```

- **Centralized**: global snap → greedy assign → sub-step converge → advance
- **Distributed**: CLAIM broadcast → conflict resolve → step → converge → advance

---

## Documentation / 文档

| 文档 | 内容 |
| :--- | :--- |
| [Algorithm / 算法详解](docs/ALGORITHM.md) | Matching, dynamics & collision avoidance algorithms |
| [Project Status / 项目进度](docs/planning/PROJECT_STATUS.md) | Milestones, changelog, current state |
| [Project Plan / 总计划](docs/planning/PROJECT_PLAN.md) | Roadmap & milestone overview |

---

## License / 许可

MIT — see [LICENSE](LICENSE)
