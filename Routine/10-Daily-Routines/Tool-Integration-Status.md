# 工具集成状态检查

> **执行时间**：每日或每次发现工具异常时
> **预计耗时**：3-5 分钟
> **目的**：主动验证各工具/插件/MCP 的可用状态，而非被动等待失败

---

## 检查清单

### 1. 内置工具 (Kimi Core)
- [ ] `Bash` - Shell 执行正常
- [ ] `Read` / `Edit` / `Write` - 文件操作正常
- [ ] `PythonRun` - 代码执行正常
- [ ] `Cron` - 定时任务系统正常
- [ ] `Agent` - 子智能体委派正常

### 2. 数据工具 (Kimi Data Tools)
- [ ] `kimi_search_v2` - 搜索可用
- [ ] `kimi_fetch_v2` - 网页抓取可用
- [ ] `kimi_finance_v2` - 金融数据可用
- [ ] `kimi_datasource_get_desc_v2` / `call_v2` - 数据源 API 可用

### 3. 插件 MCP 工具
- [ ] `kimi-webbridge` 系列 - 浏览器控制可用
- [ ] `scholar` / `yahoo_finance` / `imf` 等数据源 - 连接正常
- [ ] 自定义 MCP 工具（如有）- 状态正常

### 4. 外部集成
- [ ] WebBridge daemon 运行状态
- [ ] API Key 有效期与配额
- [ ] Python 包依赖完整性

---

## 自动化检查脚本模板

如需在 Agent 内部自动执行，可保存为 Python 脚本：

```python
def check_tool_health(ctx):
    """快速检查核心工具可用状态，返回状态报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "tools": {}
    }
    # 实际检查逻辑由 Agent 调用工具实现
    return report
```

---

## 工具降级预案

| 工具 | 降级方案 |
|------|----------|
| `kimi_search_v2` 不可用 | 使用 `kimi_fetch_v2` 直接访问已知 URL |
| `PythonRun` 超时 | 拆分为更小的子任务，使用 `Agent` 并行处理 |
| WebBridge 断开 | 提示用户手动操作，或缓存页面内容 |
| MCP 工具失效 | 使用原生 Kimi 工具链替代 |

---

## 状态记录

| 日期 | 检查工具数 | 失败工具 | 修复措施 |
|------|------------|----------|----------|
| | | | |

