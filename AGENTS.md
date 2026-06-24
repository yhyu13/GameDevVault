# AGENTS.md

Obsidian 个人知识库 —— 游戏引擎程序员的学习、沉淀与连接闭环。

## Setup commands

- 克隆仓库（含子模块）：`git clone --recurse-submodules <repo-url>`
  - 仅克隆主仓后再补子模块：`git submodule update --init --recursive`
- 拉取某个子模块更新：`git submodule update --remote <path>`
- 在 Obsidian 中打开本目录作为 Vault；根目录的 `00-README.md` 是导航入口。
- 本仓库**没有** `package.json` / `Cargo.toml` / `pyproject.toml` ——不要执行 `npm install` / `pnpm dev` / `pytest` 之类的命令。

## Vault layout

- `00-README.md` — Vault 总入口
- `知识图谱-MOC.md` — 网状导航中心（MOC），所有领域笔记的根索引
- `01-论文笔记库/` — 图形学与算法论文精读
- `02-引擎源码分析库/` — 引擎架构拆解与源码追踪（关联 `Rendering/`、`Unreal/` 子模块）
- `03-Shader与特效案例集/` — Shader 代码片段与材质案例
- `04-性能优化备忘录/` — 性能瓶颈与 Profile 解决方案
- `05-技术雷达/` — 新技术 / 工具 / 语言跟踪
- `06-职业复盘日志/` — 面试、Code Review、技术交流复盘
- `07-日记/` — 每日进度追踪与周复盘
- `99-Templates/` — 全局模板库（论文笔记 / 源码分析 / Shader / 性能优化 / 每日日记 / 周复盘 / 面试复盘 / 技术雷达条目）
- `Career/` — 职业相关长文（Kimi 输出、面试题等）
- `DigiPen/` — DigiPen 学习材料归档
- `GameEngine/` — 引擎相关额外材料
- `parallelism/` — 并行计算专题
- `Rendering/`、`Unreal/` — 通过 git submodule 引入的外部代码仓库，**不要在主仓提交它们的代码**
- `.obsidian/`、`99-Assets/` — 已在 `.gitignore`，本地配置不进版本库

## Note conventions

每条笔记的 frontmatter（参考 `99-Templates/`）：

```yaml
---
tags: [<category>/<status>]    # 例：paper/signed、source/浅度浏览、diary/周一、radar/P1
aliases: []                     # Obsidian 别名，便于反向链接
---
```

- **双向链接优先**：用 `[[链接]]` 串联相关概念，正文第一次提到某核心概念时必须加链。
- **以我为主**：不是搬运工，必须写出「对我的工作/项目有什么启发」。
- **状态用 tag 表达**：例如 `paper/待复现`、`paper/signed`、`source/浅度浏览`、`source/已应用到工作`，不要用正文里"是 / 否"复选框去表达状态。
- **跨笔记链接必填**：每篇笔记末尾的「关联 / 输出产物」段落必须填写 `[[相关笔记]]`。
- **孤立笔记是债务**：在 Obsidian 图谱视图（`Ctrl+G`）里看到没有入链也没有出链的节点，要补连接或合并。

## Knowledge workflows

| 任务 | 入口模板 | 输出位置 |
|------|---------|---------|
| 读一篇论文 | `99-Templates/论文笔记.md` | `01-论文笔记库/<作者-年份-标题>.md` |
| 分析一段引擎源码 | `99-Templates/源码分析.md` | `02-引擎源码分析库/<引擎-模块-主题>.md` |
| 收藏一个 Shader / 特效 | `99-Templates/Shader案例.md` | `03-Shader与特效案例集/<分类>/<名称>.md` |
| 记录性能优化 | `99-Templates/性能优化.md` | `04-性能优化备忘录/<场景>.md` |
| 跟踪新技术 | `99-Templates/技术雷达条目.md` | `05-技术雷达/<技术名>.md` |
| 面试或交流复盘 | `99-Templates/面试复盘.md` | `06-职业复盘日志/<日期-主题>.md` |
| 每日记录 | `99-Templates/每日日记.md` | `07-日记/<年>/<月>/<日期>.md` |

「**输入（Input）→ 输出（Output）→ 连接（Connection）**」三段式是 `07-日记/` 的硬约束，周三必填「游戏开发者视角」。

## Submodule 注意事项

- `Rendering/`、`Unreal/` 是子模块，**主仓里只读**；修改应进入对应子模块仓提交。
- 不要新增子模块（提交 `360b55f` 已说明：doc repo 用子模块体验不佳）；如确需引用外部代码仓库，直接在 markdown 里贴链接。
- 不要在主仓修改 `Rendering/Repo/`、`Unreal/LearningUnrealEngine/` 内的源码——它们会被 `git submodule update` 覆盖。

## PR & commit conventions

- 默认分支：`master`（基于 `origin/HEAD`）。
- 永远从 `master` 新建分支，**不要直接 push 到 `master`**。
- Commit message 用 conventional commits：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`。
  - 笔记类提交用 `docs:`，例如 `docs(paper): add 2024 Lumen GI paper notes`。
- 一次提交聚焦一个知识领域；不要把论文笔记和源码分析混在一个 commit 里。
- 用 `gh pr create` 打开 PR，标题形如 `docs(<area>): <short summary>`。

## Security

- 任何 API key、token、账号密码都不能写进笔记；如果要记录外部资源链接，确认是公开可访问的地址。
- `.obsidian/`、`99-Assets/`、`.trash/` 已在 `.gitignore`，不要 `git add -f` 强制提交。
- GDC Vault、SIGGRAPH 等付费资料的截图 / PDF 链接仅记录公开摘要版，不要把完整付费内容入库。