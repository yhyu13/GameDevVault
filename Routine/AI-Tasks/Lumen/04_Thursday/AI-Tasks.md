---
tags: [routine/AI-tasks, topic/Lumen, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Lumen 工程化与工具链

> **人类目标**：理解 Lumen 的底层工程实现（C++ 多线程、内存管理、工具脚本），为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释 C++ 概念、review 架构，绝不替你做核心设计。

---

## 任务 1：Lumen 相关工具脚本生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，批量检查项目中的纹理尺寸是否符合 Lumen Surface Cache 的要求（如不超过 1024x1024，且是 2 的幂次）"

**AI 输出**：完整的 Python 脚本，包含：
- 文件遍历逻辑
- 图像尺寸读取（Pillow）
- 检查规则（≤1024, power-of-2, 正方形等）
- 输出报告（CSV 或 Markdown 表格）
- 错误处理

**示例输出**：
```python
#!/usr/bin/env python3
"""
Lumen Surface Cache Texture Validator
检查纹理是否符合 Surface Cache 的硬件要求
"""

import os
from pathlib import Path
from PIL import Image
import csv

def validate_texture(path: Path) -> dict:
    """检查单个纹理是否符合 Surface Cache 要求"""
    result = {"path": str(path), "valid": True, "errors": []}
    
    try:
        with Image.open(path) as img:
            w, h = img.size
            # 检查尺寸上限
            if w > 1024 or h > 1024:
                result["valid"] = False
                result["errors"].append(f"Size {w}x{h} exceeds 1024 limit")
            # 检查 2 的幂次
            if not (is_power_of_2(w) and is_power_of_2(h)):
                result["valid"] = False
                result["errors"].append("Not power-of-2")
            # 检查正方形（Surface Cache 常用）
            if w != h:
                result["errors"].append("Not square (warning)")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Failed to open: {e}")
    
    return result

def is_power_of_2(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

# ... main() 函数遍历目录并输出 CSV
```

**你必须做**：
1. 逐行阅读代码，确保理解每个函数
2. 检查是否有引擎特定假设（如纹理格式、路径约定）
3. 添加你自己的需求（如检查是否已压缩、alpha 通道等）
4. 运行并验证输出

---

## 任务 2：C++ 概念解释 — Lumen 相关（AI 执行，你实践）

**输入**：你遇到的具体 C++ 概念，如 "Lumen 的 Job System 中 Task Graph 是如何保证 RenderThread 和 GameThread 同步的？"

**AI 输出**：
1. **概念解释**：用类比 + 代码示例解释
2. **在 Lumen 中的具体应用**：指出 UE5 源码中的相关文件和函数
3. **常见问题**：race condition、deadlock、false sharing
4. **练习建议**：一个迷你编程题让你实践

**示例**：
> **Task Graph 解释**：Task Graph 就像一个餐厅厨房的点餐系统。主厨（GameThread）下单，各工作站（Worker Threads）并行处理，最后通过依赖关系（边）确保"上菜顺序"正确。Lumen 的 Card Update 和 Mesh SDF Generation 就是通过 Task Graph 并行的。

**你必须做**：
1. 在 UE5 源码中找到 Task Graph 的使用点（`FTaskGraphInterface`）
2. 写一个自己的迷你 Task Graph 示例（不依赖 UE5，用 std::async 或 thread pool）
3. 用 Intel VTune 或 Tracy 观察并行效果

---

## 任务 3：Lumen 架构 Review（AI 执行，你决策）

**输入**：你设计的自研引擎 GI 架构文档（或头脑风暴文字）

**AI 审查清单**：
- [ ] 是否考虑了多线程安全？（Lumen 的 GameThread/RenderThread/RHIThread 分离）
- [ ] 内存分配策略是否合理？（Surface Cache 的纹理池管理）
- [ ] 是否有动态扩容/缩容机制？（Radiance Cache 的自适应分配）
- [ ] 错误处理路径是否完整？（SDF 生成失败 fallback）
- [ ] 与现有系统的耦合度？（是否侵入式修改渲染管线）
- [ ] 平台兼容性？（移动端是否需要关闭 Lumen 并 fallback 到烘焙）

**AI 输出**：架构审查报告，指出潜在风险和改进建议

**你必须做**：评估每个建议的优先级，决定是否采纳。AI 不懂你的项目约束（工期、团队规模、目标平台），最终决策权在你。

---

## 任务 4：内存布局分析（AI 执行，你计算）

**输入**：Lumen 中某个结构体的定义（从 UE5 源码复制）

**AI 输出**：
1. 每个字段的大小和对齐分析
2. 结构体总大小（含 padding）
3. Cache Line 分析（是否跨 Cache Line）
4. 优化建议（字段重排序减少 padding）

**示例**：
```cpp
struct FLumenCard {
    FVector4 Center;        // 16 bytes (SIMD aligned)
    FVector4 Orientation;   // 16 bytes
    float MinZ, MaxZ;       // 8 bytes (but needs padding to 16)
    uint32 MeshIndex;       // 4 bytes
    uint16 Resolution;      // 2 bytes
    // ... padding here?
};
```

**AI 分析**：
> 当前布局：64 bytes → 对齐到 64 bytes（1 Cache Line）✓  
> 建议：将 `MinZ, MaxZ` 提前到 `Center` 之后，可减少 padding。

**你必须做**：用 `sizeof()` 和 `offsetof()` 实际验证 AI 的计算。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计整个 GI 架构
- ❌ 直接运行 AI 生成的脚本而不 review
- ❌ 让 AI 解释 C++ 后你不写代码实践
- ❌ 盲目采纳 AI 的架构建议（不考虑项目约束）

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] C++ 概念已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已用 `sizeof()` 验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 个工具脚本 + 1 个 C++ 实践 + 1 份架构审查 + 1 次内存分析*
