---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Unreal MCP 工程化与工具链

> **人类目标**：理解 Unreal MCP 的编辑器集成、安全模型和自定义工具开发。  
> **AI 任务**：生成工具脚本、解释架构、review 安全模型，绝不替你做核心设计。

---

## 任务 1：MCP 工具注册脚本生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，自动生成 MCP Tool Schema JSON 文件，从给定的函数签名中提取参数名、类型和文档字符串"

**AI 输出**：完整的 Python 脚本

**示例输入**：
```python
def get_scene_objects(object_type: str, max_count: int = 100) -> list:
    """Get objects in the current scene by type."""
    pass

def modify_blueprint(blueprint_path: str, property_name: str, value: str) -> bool:
    """Modify a property in a Blueprint."""
    pass
```

**AI 生成的脚本应输出**：
```json
{
  "tools": [
    {
      "name": "get_scene_objects",
      "description": "Get objects in the current scene by type.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "object_type": {"type": "string"},
          "max_count": {"type": "integer", "default": 100}
        },
        "required": ["object_type"]
      }
    }
  ]
}
```

**你必须做**：
1. 逐行阅读代码
2. 检查类型映射是否正确（Python type → JSON Schema type）
3. 添加默认值、枚举、嵌套对象的支持
4. 运行并验证输出

---

## 任务 2：MCP 安全模型概念（AI 执行，你实践）

**输入**："Unreal MCP 的权限模型如何防止 AI 误删资产？MCP 的 Roots 和 Sampling 机制是什么？"

**AI 输出**：
1. **Roots**：AI 只能在指定目录/范围内操作（类似 chroot）
2. **Sampling**：AI 读取文件前需要用户确认（类似 sudo）
3. **Unreal MCP 的额外限制**：Editor 模块只能在 Editor 模式下运行，不能用于打包游戏

**你必须做**：
1. 阅读 MCP 规范的 Security 章节
2. 设计一个 "安全策略" 文档：列出 AI 应该能做什么、不能做什么
3. 为 Unreal MCP 设计一个最小权限模型（例如：AI 可以查询场景，但不能删除 Level，除非用户显式确认）

---

## 任务 3：Unreal MCP 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持多 Client 同时连接？（并发安全）
- [ ] Transport 层是否支持 WebSocket / SSE？（实时推送）
- [ ] Tool 执行是否异步？（避免阻塞 Editor 主线程）
- [ ] 错误日志是否足够详细？（调试 AI 行为）
- [ ] 是否支持 Tool 热更新？（不重启 Server 添加新工具）
- [ ] 与现有编辑器脚本系统（PythonScriptPlugin、EditorUtilityWidgets）的兼容性？

**你必须做**：评估每个建议，记录决策。

---

## 任务 4：MCP 消息内存布局分析（AI 计算，你验证）

**输入**：MCP 消息结构体（简化版）

```cpp
struct MCPMessage {
    FString JsonRpc;          // "2.0" — 5 chars
    int32 Id;                 // 4 bytes
    FString Method;           // 变长
    TSharedPtr<FJsonObject> Params;  // 共享指针
    TSharedPtr<FJsonObject> Result;  // 共享指针
    TSharedPtr<FJsonObject> Error;   // 共享指针
};
```

**AI 输出**：内存大小估算、TSharedPtr 开销分析、消息序列化建议

**你必须做**：用 `sizeof()` 或 `UE_LOG` 测量实际消息大小，对比 AI 估算。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计安全模型（安全必须你自己思考）
- ❌ 直接运行脚本不 review（安全脚本尤其重要）
- ❌ 解释概念后不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] 安全模型文档已手写（AI 不能替你决策安全）
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
