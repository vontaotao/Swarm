# 目标 002: 动态快照 + 基础可视化

## 状态

✅ 已完成 (2026-05-22)

## 目标描述

在核心匹配引擎之上加入三个能力：动态快照序列、matplotlib 可视化、无人机速度约束。

## 验收标准

- [x] choreographer.py 支持 4 种动态模式（line_sweep / circle_shift / pulse / diagonal）
- [x] visualizer.py 将轨迹渲染为 GIF，含目标像素、无人机点、编号、时间戳
- [x] Drone 支持 `max_speed` 和 `move_toward()`，`max_speed=inf` 时与 `move_to()` 等价
- [x] Simulation `run()` 加入内层收敛循环，速度约束时迭代匹配+渐进移动
- [x] 全部现有测试通过，无回归，新增 20 项测试

## 技术决策

- **内层收敛循环**：每时间步内重复 match + move_toward 直到所有无人机到达目标
- **max_speed=inf 退化为瞬时**：向后兼容，默认行为不变
- **matplotlib Agg 后端**：无需 GUI，纯脚本渲染
- **4 种模式用注册表分派**：`_PATTERNS` 字典，易于扩展

## 测试结果

```
55 passed in 0.45s
```
