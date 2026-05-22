# Swarm — 无人机群空间快照补位仿真

中央电脑每个时间步发布"空间快照"（目标编队的空间分布），无人机群基于 **最近邻原则** 自动就近补位，形成目标编队。

## 核心算法

```
t 时刻:
  1. 在位检测 — 无人机当前位置是否已在目标像素上
  2. 空缺收集 — 收集所有未被填充的目标像素
  3. 距离优先贪心分配 — 按最近空缺距离升序排列，依次匹配
  4. 收敛 → 推进到 t+1
```

## 项目结构

```
src/
├── grid.py          # 2D 空间网格 + 编队图案生成（矩形/圆/空心圆）
├── drone.py         # 无人机个体
├── matcher.py       # 最近邻贪心匹配（核心）
└── simulation.py    # 主仿真循环
tests/               # 对应单元测试
docs/planning/       # 项目规划文档
```

## 快速开始

```bash
# 安装依赖
pip install numpy pytest

# 运行全部测试
python -m pytest tests/ -v

# 运行示例仿真
python -c "
from src.grid import create_snapshot_rectangle, create_snapshot_hollow_circle
from src.simulation import run

snapshots = [
    create_snapshot_rectangle(40, 40, 10, 10, 8, 6),
    create_snapshot_hollow_circle(40, 40, 30, 30, 5, 10),
]
trajectory = run(snapshots, n_drones=10, seed=42)
"
```

## 进度

- [x] 里程碑 1：核心仿真引擎（grid / drone / matcher / simulation）
- [ ] 里程碑 2：动态快照序列 + matplotlib 可视化
- [ ] 里程碑 3：3D 扩展 + 通信模型
- [ ] 里程碑 4：硬件接口（MAVLink / ROS）

详见 `docs/planning/PROJECT_STATUS.md`

## 许可

MIT — 见 [LICENSE](LICENSE)
