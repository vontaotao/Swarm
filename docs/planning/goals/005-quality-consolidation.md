# 目标 005: 工程质量夯实

## 状态

已完成 (2026-05-25)

## 目标描述

不增加新功能，专注修复已知 bug、暴露硬编码参数、补充边界测试覆盖。

## 验收标准

- [x] physics.py 属性优先级反转修复（config 优先 → drone 回退）
- [x] simulation.py 硬编码 _MAX_SUB_STEPS 暴露为 max_sub_steps 参数 + 超时警告
- [x] distributed_matcher.py 硬编码 _MAX_ROUNDS 暴露为 max_rounds 默认值 + verbose + 超时警告
- [x] visualizer.py slice_z 防御检查
- [x] 测试覆盖 124 → 139 项（+15 项）
- [x] 零外部依赖变更

## 技术决策

- **config-first 优先级**：physics_step 中 config 显式传入的值优先于 drone 持久属性，因为 config 是调用者每步的意图
- **暴露而非删除**：max_sub_steps / max_rounds 作为默认参数暴露，保持向后兼容
- **超时警告非错误**：循环耗尽时仅打印警告（verbose=True），不抛异常
- **边界防御**：visualizer slice_z 越界显式报错，优于 IndexError

## 改动清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| src/physics.py | Bug Fix | 优先级反转 3 行 |
| src/simulation.py | 重构 | 常量 → 参数，超时警告，透传 max_rounds/verbose |
| src/distributed_matcher.py | 重构 | 删除 _MAX_ROUNDS，+verbose，超时警告 |
| src/visualizer.py | 防御 | slice_z bounds check |
| tests/test_physics.py | +6 | 优先级 + 边界 |
| tests/test_simulation.py | +3 | max_steps + 全 True 网格 |
| tests/test_drone.py | +1 | max_speed=0 |
| tests/test_grid.py | +2 | 负坐标 |
| tests/test_distributed_matcher.py | +1 | 3D 空快照 |
| tests/test_visualizer.py | +2 | 3D 渲染 + 越界 |

## 测试结果

```
139 passed in 1.08s
```
