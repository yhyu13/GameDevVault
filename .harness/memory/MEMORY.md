# GameDevVault Team Memory

> 跨 session 共享的 vault 元信息。新增一条笔记或改动 vault 结构后在这里更新一行。

## Vault 元信息

- 仓库：GameDevVault（Obsidian vault for game engine programming）
- 主仓默认分支：`master`
- 笔记语言：中文为主，模板里的关键词同时保留英文（frontmatter 字段、tag 前缀）。
- 模板库：`99-Templates/`（论文笔记 / 源码分析 / Shader 案例 / 性能优化 / 每日日记 / 周复盘 / 面试复盘 / 技术雷达条目）
- 根索引：`知识图谱-MOC.md`
- 总入口：`00-README.md`
- 外部代码子模块：`Rendering/`（Ray Tracing Gems、DirectX-Graphics-Samples、ZetaRay、vk_raytrace、hybrid-rendering）、`Unreal/LearningUnrealEngine/`

## 当前领域覆盖（粗略盘点，后续按需细化）

- 渲染管线：MOC 顶层有占位，详细单笔记按需补
- 引擎架构：MOC 顶层有占位
- 性能优化：MOC 顶层有占位
- 数学与算法基础：MOC 顶层有占位
- 前沿技术雷达：MOC 顶层有占位
- 职业发展：MOC 顶层有占位

## 团队约定（所有 rein 共享）

- 写笔记用 Edit / Write 工具，不走 PowerShell `Set-Content`（中文 vault 走 ANSI 编码会损坏 UTF-8）。
- tag 词表见 `.harness/docs/vault-conventions.md`，新增 tag 类型前先在那里登记。
- 文件命名：英文场景用 kebab-case，中文场景用中文短语，整目录内风格一致。
- 不要把付费资料完整 PDF 入库；只存公开摘要链接。

## 已知陷阱

- 不要新增 git submodule（提交 `360b55f` 已说明 doc repo 体验差）。
- 不要在主仓修改 `Rendering/`、`Unreal/` 子模块内代码——会被 `git submodule update` 覆盖。
- 不要把状态信号（待复现 / P1 / 已复现）写成 `[x]` 复选框；用 tag。