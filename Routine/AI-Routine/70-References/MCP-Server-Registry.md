# MCP Server 注册表

> **目标**：记录所有可用的 MCP 工具及其状态，作为工具选择参考
> **更新频率**：每次新增/移除/变更 MCP 时

---

## 内置 MCP 插件

| 插件名 | 状态 | 用途 | 核心工具 | 优先级 |
|--------|------|------|----------|--------|
| `kimi-webbridge` | ✅ 可用 | 浏览器控制 | `navigate`, `snapshot`, `click`, `fill`, `evaluate` | 高 |
| `scholar` | ✅ 可用 | 学术文献 | `kimi_datasource_get_desc_v2`, `kimi_datasource_call_v2` | 中 |
| `yahoo_finance` | ✅ 可用 | 金融数据 | 同上 | 中 |
| `imf` | ✅ 可用 | 宏观经济 | 同上 | 低 |
| `sec_edgar` | ✅ 可用 | SEC 数据 | 同上 | 低 |
| `ifind` | ✅ 可用 | 中国金融 | 同上 | 中 |
| `tianyancha` | ✅ 可用 | 企业数据 | 同上 | 低 |
| `yuandian_law` | ✅ 可用 | 法律数据 | 同上 | 低 |
| `world_bank_open_data` | ✅ 可用 | 世行数据 | 同上 | 低 |

---

## 原生 Kimi 工具

| 工具 | 类型 | 用途 | 限制 | 备注 |
|------|------|------|------|------|
| `Bash` | 执行 | Shell 命令、管道、Git | 60-300s 超时 | 优先用 Read/Edit 做文件操作 |
| `Read` | 读取 | 文件内容读取 | 1000 行/100KB 限制 | 支持 line_offset 分页 |
| `Edit` | 编辑 | 增量文本替换 | old_string 必须唯一 | 编辑前必读 |
| `Write` | 写入 | 创建/覆盖文件 | 不可用于增量编辑 | 父目录必须存在 |
| `Glob` | 搜索 | 文件路径查找 | 最多 100 结果 | 避免递归 node_modules |
| `Grep` | 搜索 | 内容搜索 | 250 行输出限制 | 优先于 shell grep |
| `PythonRun` | 执行 | Python 代码即时运行 | 定义 main(ctx) 函数 | 图表用 setup_plot(ctx) |
| `Cron` | 调度 | 定时任务 | 仅 local_conversation | 精确表达需确认 |
| `Agent` | 委派 | 子智能体 | 30min 超时 | 优先 resume |
| `SystemInvoke` | 系统 | 调用注册系统工具 | 检查可用性 | 配合 SystemList |
| `kimi_search_v2` | 数据 | 网络搜索 | 第三方数据 | 当前搜索 |
| `kimi_fetch_v2` | 数据 | URL 内容获取 | 解码限制 | 非结构化数据 |
| `kimi_finance_v2` | 数据 | 股票数据 | 仅市场数据 | 非投资建议 |
| `SkillManage` | 技能 | 技能 CRUD | 路径权限 | 技能管理 |
| `TodoList` | 任务 | 待办追踪 | 不跨会话 | 主动更新 |
| `ReadMediaFile` | 媒体 | 图片/视频读取 | 100MB 限制 | 媒体分析 |

---

## 自定义工具/脚本

| 工具名 | 路径 | 类型 | 状态 | 用途 | 备注 |
|--------|------|------|------|------|------|
| | | | | | |

---

## 工具选型决策树

```
需要文件操作？
├── 已知路径 → Read / Edit / Write
│   └── 增量编辑 → Edit（优先）
│   └── 新文件 → Write
└── 未知路径 → Glob / Grep

需要代码执行？
├── Python → PythonRun
├── Shell → Bash
└── 复杂/耗时 → Agent（子智能体）

需要外部数据？
├── 网页 → kimi_fetch_v2
├── 搜索 → kimi_search_v2
├── 金融 → kimi_finance_v2
└── 特定数据源 → MCP 对应插件

需要浏览器？
└── kimi-webbridge（MCP）

需要定时？
└── Cron（仅 local_conversation）
```

---

## 注册表变更日志

| 日期 | 操作 | 工具名 | 原因 | 负责人 |
|------|------|--------|------|--------|
| | | | | |
