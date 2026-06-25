# 晨间 Agent 健康检查

> **执行时间**：每次启动 Kimi Work / 开始工作前
> **预计耗时**：2-5 分钟
> **目的**：确认 Agent 自身工具链、环境、状态正常，避免在编码中途发现工具不可用

---

## 检查清单

### 1. 环境状态检查
- [ ] Kimi Work 版本与插件状态正常
- [ ] 当前 Workspace 路径正确 (`D:\GitRepo-My\AIResearchVault\document`)
- [ ] Python 运行时可用 (`~/.kimi/daimon/runtime/python`)
- [ ] Git Bash 路径归一化正常 (`pwd -W` → Windows path)

### 2. 工具链可用性检查
- [ ] **MCP Servers**：检查已注册的 MCP 工具列表 (`SystemList`)
- [ ] **WebBridge**：确认 daemon 可连接 (`http://127.0.0.1:10086`)
- [ ] **DataSource APIs**：确认至少一个数据源可用 (`kimi_search_v2`, `kimi_fetch_v2`)
- [ ] **Cron 系统**：检查是否有待执行或执行失败的定时任务

### 3. 记忆与上下文检查
- [ ] Vault Memory 正确加载 (`about_user.md` 状态)
- [ ] 技能索引已加载，无缺失
- [ ] 昨日会话上下文已归档，无异常

### 4. 外部依赖检查
- [ ] 网络连接正常（如需搜索/抓取）
- [ ] API Key 有效（KIMI_API_KEY / agent-gw.json）
- [ ] 磁盘空间充足（日志、输出文件）

---

## 快速诊断命令

```bash
# 检查当前时间与路径
date '+%Y-%m-%dT%H:%M:%S%z (%Z)'
pwd -W

# 检查 Kimi 运行时 Python
python -c "import sys; print(sys.executable)"

# 检查 WebBridge 状态（如果可用）
curl -s http://127.0.0.1:10086/command 2>nul && echo "WebBridge OK" || echo "WebBridge OFF"
```

---

## 异常处理流程

| 异常 | 处理措施 |
|------|----------|
| MCP 工具缺失 | 检查插件安装状态，重启 Kimi Work |
| WebBridge 未连接 | 手动启动 daemon（见 `kimi-webbridge` skill） |
| API Key 失效 | 检查 `~/.kimi/agent-gw.json` 或环境变量 |
| Vault Memory 损坏 | 从备份恢复，或重建 `about_user.md` |
| 磁盘空间不足 | 清理 `80-Experiments/` 旧实验，归档日志 |

---

## 记录

| 日期 | 检查人 | 状态 | 异常 | 处理结果 |
|------|--------|------|------|----------|
| | | | | |

