# 项目当前状态

## 当前阶段

**里程碑 2: 动态快照 + 基础可视化** — 已实现。

## 已完成

### 里程碑 1: 核心仿真引擎
- [x] `src/grid.py` — 2D 空间网格 + 快照生成（矩形、圆形、空心圆、自定义点位）
- [x] `src/drone.py` — 无人机个体（ID、位置、距离计算、瞬时移动、速度约束）
- [x] `src/matcher.py` — 最近邻贪心匹配算法（在位检测 → 空缺收集 → 距离优先分配）
- [x] `src/simulation.py` — 主仿真循环（多步推进、轨迹记录、内层收敛循环）
- [x] 对应测试套件

### 里程碑 2: 动态快照 + 基础可视化
- [x] `src/choreographer.py` — 动态快照序列生成（line_sweep / circle_shift / pulse / diagonal）
- [x] `src/visualizer.py` — matplotlib GIF 渲染（目标像素 + 无人机点 + 编号 + 时间戳）
- [x] Drone 添加 `max_speed` 属性和 `move_toward()` 方法（保留 `move_to()`）
- [x] Simulation 添加内层收敛循环，支持速度约束模式
- [x] 全部 55 项测试通过

## 下一步

- 里程碑 3 规划：3D 扩展 + 通信模型
- 当前可执行 `python -m pytest tests/ -v` 验证全部测试
- 运行示例仿真并生成 GIF：
  ```python
  from src.choreographer import generate_sequence
  from src.simulation import run
  from src.visualizer import render_gif
  seq = generate_sequence(60, 60, 25, 'circle_shift', radius=6)
  traj = run(seq, n_drones=12, max_speed=2.5, seed=42)
  render_gif(traj, seq, 'swarm_demo.gif', fps=6)
  ```

## 风险

（暂无）
