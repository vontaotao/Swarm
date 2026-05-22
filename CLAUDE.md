# CLAUDE.md

## 0. 基础规则

- 所有对话、解释、代码注释、提交说明优先使用中文

- 代码必须保持高解耦：一个功能对应一个独立文件或模块

- 每个代码文件顶部必须包含详细注释，说明：1、本文件的功能是什么。2、输入是什么。3、输出是什么。4、核心执行流程是什么。5、依赖哪些外部模块或数据。

- 开始任何代码或文档变更前，必须先阅读 `docs/planning/PROJECT_STATUS.md`，再按需阅读 `docs/planning/PROJECT_PLAN.md`、相关 `docs/planning/goals/*.md` 和 `docs/TEAM_WORKFLOW.md`。

- 项目规划采用渐进式披露：`PROJECT_STATUS.md` 是当前进度上下文，`PROJECT_PLAN.md` 是总计划，`goals/*.md` 是单目标细案，`TEAM_WORKFLOW.md` 是团队协作与规划合并规则；如果它们与归档旧计划冲突，以当前规划文件为准。

- 规划文件维护必须遵循 `docs/TEAM_WORKFLOW.md`：只有当任务改变目标状态、下一步、风险、验证结果或团队决策时，才同步更新对应规划文件；不要把 `PROJECT_STATUS.md` 当作每次对话都必须追加的工作日志。

---


Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.