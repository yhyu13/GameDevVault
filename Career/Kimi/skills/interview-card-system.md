# Skill: 游戏开发面试知识卡牌化系统

> **版本:** 1.0  
> **路径:** `C:\Git-repo-my\GameDevVault\Career\Kimi\skills\`  
> **适用场景:** 将技术博客/源码分析转化为面试速查材料 + 互动测试  
> **创建者:** 俞航（用于 JD：游戏开发专家 AI 训练方向）

---

## 一、目标

将任何技术资料（源码分析、论文、官方文档）快速转化为三层面试准备材料：
1. **Concept Card（轻量索引）** — 面试前 30 分钟速读，一句话答案 + 打油诗
2. **Detail（技术详情）** — 面试前 2 小时深入，源码位置 + 代码片段 + 深度解析
3. **HTML 互动卡牌** — 自测工具，拖拽填空 + 单选 + 多选 + **判断题** + 总览面板 + 打分系统
4. **综合 Detail HTML** — 跨模块深度面试，覆盖源码、追问、性能分析、调试技巧

---

## 二、输入

- 技术博客/源码分析文章（如 timlly《剖析虚幻渲染体系》）
- Epic 官方白皮书/技术文档
- 论文/论坛讨论
- **个人项目经验**（Cook 优化、Shader 调试、性能分析等）

---

## 三、输出目录结构

```
Career/
  Kimi/
    ├── UE5_Nanite_timlly.md      ← 原始资料整理（Part 1）
    ├── UE5_Lumen_timlly.md       ← 原始资料整理（Part 2）
    ├── UE5_Concept_Cards.md      ← 轻量索引（所有模块的一句话答案）
    ├── UE5_Detail.md             ← 技术详情（源码 + 代码片段 + 解析）
    ├── html/
    │     ├── nanite/
    │     │     └── index.html    ← Nanite 模块卡牌（自包含）
    │     ├── lumen/
    │     │     └── index.html    ← Lumen 模块卡牌
    │     ├── vsm/
    │     │     └── index.html    ← VSM 模块卡牌
    │     └── ue5-detail/         ← 新增：综合 Detail 面试卡牌
    │           └── index.html    ← 跨模块深度面试（源码/追问/性能）
    └── skills/
          └── interview-card-system.md  ← 本 Skill 文档
```

---

## 四、工作流程（5 步法）

### Step 1：资料获取与整理
- 读取技术博客/源码分析，用 Markdown 整理核心内容
- 保留原始出处（作者、URL、日期）
- 标注关键源码类名和文件路径
- **标记个人经验关联点**："我在火炬项目中遇到过类似问题..."

### Step 2：Concept Card（轻量索引）
**原则：** 每个概念只留一句话答案，所有细节指向 Detail

**格式：**
```markdown
### Q{N}：{问题}
> **答：** {一句话答案}  
> **详情：** [Detail §X.X {标题}](UE5_Detail.md)
```

**每个模块必须包含：**
- 1 首打油诗（帮助记忆）
- 1 张核心概念脑图（Mermaid）
- 1 张源码速查表（类名/文件/作用）
- 3-6 个面试 Mock 题（自问自答）
- **判断题锚定点**：哪些概念最容易被面试官用"是非"形式快速测试

### Step 3：Detail（技术详情）
**原则：** 源码级深度，面试追问能答到函数名和算法细节

**每个章节必须包含：**
- 源码文件路径（如 `Engine\Source\Runtime\Nanite\Public\NaniteRender.h`）
- 代码片段 + 逐行注释
- 追问的详细答案（"How?" 层面）
- 与已掌握知识的关联（如 UE4→UE5 对比）
- 1 首打油诗（相同内容，不同角度）
- **判断题素材标记**：哪些细节是"坑"——表面看起来像对，实际上有边界条件

### Step 4：HTML 互动卡牌（两种类型）

#### 类型 A：模块卡牌（nanite/lumen/vsm）
**原则：** 聚焦单一模块，快速建立概念地图

**功能清单：**
| 功能 | 必须 | 说明 |
|------|------|------|
| 拖拽填空 | ✅ | 术语填入正确位置 |
| 单选题 | ✅ | 4 个选项，选 1 |
| 多选题 | ✅ | 6 个选项，选 N |
| **判断题** | ✅ | 是/否，快速筛查概念盲区 |
| 检查答案 | ✅ | 显示正确/错误 + 逐选项解析 |
| 重置题目 | ✅ | 可重新答题 |
| **随机打乱** | ✅ | 打乱题目顺序 + 单选/多选选项顺序，每次重新洗牌 |
| 总览面板 | ✅ | 缩略图网格 + 筛选（正确/错误/未答） |
| 打分系统 | ✅ | 实时显示总得分 |
| 重置全部 | ✅ | 清空所有答题记录 |
| 跨题型跳转 | ✅ | 从总览面板点击跳转到任意题目 |
| 进度条 | ✅ | 当前题号 / 总题数 |
| 上一题/下一题 | ✅ | 导航按钮 |
| 自适应布局 | ✅ | 支持手机/平板/桌面 |

#### 类型 B：综合 Detail 面试卡牌（ue5-detail）
**原则：** 跨模块深度面试，源码 + 追问 + 性能 + 调试

**特点：**
- 不用于"概念速记"，用于"深度面试模拟"
- 题目从 `UE5_Detail.md` 中提炼，包含源码、算法、边界条件
- 题型：单选 + 多选 + 判断（不做拖拽，因为跨模块不适合术语填空）
- 覆盖：Nanite + Lumen + VSM + Render Graph + GPUScene + Strata + 性能优化
- 每题附带"追问链"：回答正确后显示可能的面试官追问

### Step 5：验证与迭代
- 自己先做一遍 HTML 测试，确保所有答案正确
- 检查超链接（相对路径 `UE5_Detail.md`）
- 追问循环：对每个概念回答 "How?" 和 "Why?"，直到没有追问
- **判断题验证**：对每个判断题，确保"错误"选项描述的是常见误解，而非明显荒谬的表述

---

## 五、HTML 题目设计规范

### 拖拽填空题
```
题目：Nanite 将几何体数据以 {0} 为单位管理，LOD 决策在 {1} 上运行时动态完成。
答案：["Page", "GPU"]
选项池：["Page", "GPU", "CPU", "Cluster", "Texture"]
逐空解析：[
  "Page 是数据加载最小单位，不可用 Cluster 因为 Cluster 是几何单元",
  "GPU 负责运行时动态决策，CPU 只做离线构建"
]
```

### 单选题
```
题目：为什么 Nanite 需要软件光栅化？
选项：["A. 大三角形效率更高", "B. 处理亚像素微多边形...", "C. 替代硬件光栅化", "D. 处理透明材质"]
正确答案：1 (B)
选项解析：[
  "❌ 错误：大三角形用硬件光栅化效率更高",
  "✅ 正确：硬件光栅化在亚像素级时 Quad Overdraw 严重...",
  "❌ 错误：软件不是替代硬件，而是互补",
  "❌ 错误：Nanite 不支持透明材质"
]
```

### 多选题
```
题目：Nanite 的 fallback 条件包括哪些？（多选）
选项：6 个
正确答案：[0, 1, 2, 3, 5] (索引数组)
选项解析：每个选项单独解析
```

### **判断题（新增）**
**设计原则：** 判断题不是"考记忆力"，而是"筛查概念盲区"。错误的陈述必须是面试中常见的**似是而非的误解**。

```
题目：Nanite 和 VSM 共享主相机的视锥裁剪结果。
正确答案：false
解析：
  ✅ 正确理解：共享的是图元级数据（GPUScene 实例变换），但视图级裁剪（Frustum/HZB）是独立执行的——主相机和 Light Camera 的视锥不同。
  ❌ 常见误解：误以为 GPU-Driven 意味着所有视角共享同一套裁剪结果。
追问：如果面试官追问"那 Draw Command 呢？"  
  答：Draw Command 也是各自独立生成的，但生成框架（InstanceCullingManager）是同一套代码。
```

**判断题错误陈述的常见设计模式：**
| 模式 | 示例 | 考察点 |
|------|------|--------|
| 混淆层级 | "Nanite 和 VSM 共享裁剪结果" | 图元级 vs 视图级 |
| 边界条件忽略 | "Lumen 支持所有材质" | Translucent 不支持 |
| 版本误判 | "Nanite 不支持骨骼动画" | 5.5+ 已支持 |
| 因果倒置 | "Mesh SDF 存储颜色信息" | SDF 只存距离 |
| 过度泛化 | "GPU-Driven 意味着 CPU 完全不参与" | CPU 仍做离线构建 |

---

## 六、综合 Detail 面试卡牌设计（ue5-detail）

### 题目来源（从 `UE5_Detail.md` 提炼）

| 来源类型 | 题目示例 | 考察维度 |
|----------|----------|----------|
| **源码函数** | "`BuildPageAllocations` 中哪一步负责缓存复用？" | 源码熟悉度 |
| **算法细节** | "Sphere Tracing 的步进距离等于什么？" | 算法理解 |
| **边界条件** | "Screen Trace 失败后回退到 Mesh SDF，如果 Mesh SDF 也失败呢？" | 回退链 |
| **性能分析** | "Lumen 的无限反弹为什么不会导致无限计算？" | 性能意识 |
| **调试技巧** | "如果 VSM 出现阴影闪烁，可能是什么问题？" | 工程经验 |
| **跨模块交互** | "Nanite 的 Cluster 数据如何驱动 VSM 的 Page 分配？" | 系统理解 |
| **对比分析** | "UE4 CSM 和 UE5 VSM 在内存占用上的本质差异？" | 架构理解 |

### 追问链设计

每道 Detail 级题目回答正确后，显示可能的追问：

```
✅ 回答正确！

面试官可能的追问：
  1. "Sphere Tracing 在什么情况下会退化成固定步长？"
     → 答：当 SDF 值极小（接近表面）时，步进距离趋于零，需要设置最小步长阈值或切换到固定步长。
  2. "如果 Mesh SDF 的分辨率不够，会出现什么 artifact？"
     → 答：漏光（light leaks）或错误遮挡，因为低分辨率 SDF 无法精确表示薄几何体。
  3. "UE5 中有没有替代 Sphere Tracing 的方案？"
     → 答：Hardware RT 是精确替代，但开销更大；也可以增加 SDF 分辨率或使用 Analytic SDF（解析距离场）。
```

---

## 七、追问迭代机制

对每个概念，必须回答以下追问：

| 追问类型 | 示例 | 回答深度 |
|----------|------|----------|
| **Why?** | 为什么叫 Virtualized Geometry？ | 概念原理 |
| **How?** | 怎么实现按需分配虚拟页？ | 算法/源码流程 |
| **What if?** | 如果三角形小于一个像素会怎样？ | 边界条件 |
| **Compare?** | 与 UE4 传统 LOD 的本质区别？ | 对比分析 |
| **Future?** | 当前限制和未来方向？ | 行业趋势 |
| **Interview?** | 如果面试官问 XX 怎么答？ | 面试话术 |
| **Debug?** | 如果线上出现 XX 问题怎么排查？ | 工程经验 |

---

## 八、快捷键/速查

| 操作 | 功能 |
|------|------|
| 点击 "📊 题目总览" | 打开总览面板 |
| 点击缩略图 | 跳转到对应题目 |
| 拖拽术语到填空位 | 提交答案 |
| 点击选项 | 选择单选/多选/判断 |
| 点击 "检查答案" | 显示解析 + 追问链（Detail 卡牌） |
| 点击 "重置" | 清空当前题 |
| 点击 "🔄 随机打乱" | 重新洗牌题目顺序 + 选项顺序 |
| 点击 "🔄 重置所有分数" | 清空全部记录 |

---

## 九、已知限制与 TODO

| 限制 | 状态 |
|------|------|
| 拖拽填空不支持触摸设备（需用点击替代） | 待优化 |
| 多选时未选中的错误选项不标红（仅标用户选中的） | 按设计保持 |
| 总览面板不支持键盘导航 | 待优化 |
| 无后端存储，刷新页面分数丢失 | 可用 localStorage 扩展 |
| 无计时功能 | 待扩展 |
| 无错题本（自动收集做错的题） | 待扩展 |
| 判断题无" unsure "选项 | 待扩展（增加"不确定"按钮） |
| Detail 卡牌追问链未实现交互式展开 | 待扩展 |
| 拖拽填空选项池无法点击选择（仅支持拖拽） | 待扩展 |

---

## 十、模板复用指南

### 随机打乱（Reshuffle）实现规范

每个模块卡牌必须支持"随机打乱"功能：

1. **打乱题目顺序**：拖拽填空、单选、多选、判断题各自的题目数组随机重排
2. **打乱选项顺序**：单选题和多选题的 `options` 数组随机重排，同时更新 `correct` 索引以指向正确答案的新位置
3. **重置分数**：打乱时自动清空所有答题记录，避免旧答案与新题序错位
4. **UI 按钮**：在 header 区域放置 `🔄 随机打乱` 按钮，与 `📊 题目总览` 并列

**实现要点：**
```javascript
// 1. 保存原始题目（只读常量）
const _origDrag = JSON.parse(JSON.stringify(dragQuestions));

// 2. 打乱数组的 Fisher-Yates 算法
function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// 3. 打乱单选/多选选项（同时映射 correct 索引）
function shuffleOptions(q) {
  const indices = q.options.map((_, i) => i);
  const shuffledIndices = shuffleArray(indices);
  const newOptions = shuffledIndices.map(i => q.options[i]);
  const newOptionExplanations = shuffledIndices.map(i => q.optionExplanations[i]);
  const newCorrect = Array.isArray(q.correct)
    ? q.correct.map(oldIdx => shuffledIndices.indexOf(oldIdx)).filter(i => i >= 0).sort((a,b)=>a-b)
    : shuffledIndices.indexOf(q.correct);
  return { ...q, options: newOptions, optionExplanations: newOptionExplanations, correct: newCorrect };
}

// 4. 全局打乱入口
function reshuffleAll() {
  // 重置所有分数
  resetAll();
  // 打乱题目顺序（深拷贝避免修改原始数据）
  dragQuestions = shuffleArray(_origDrag);
  singleQuestions = shuffleArray(_origSingle).map(shuffleOptions);
  multiQuestions = shuffleArray(_origMulti).map(shuffleOptions);
  trueFalseQuestions = shuffleArray(_origTF);
  // 重建 allQuestions
  rebuildAllQuestions();
  // 重新渲染当前题型
  if (currentMode === 'drag') renderDrag();
  else if (currentMode === 'single') renderSingle();
  else if (currentMode === 'multi') renderMulti();
  else if (currentMode === 'tf') renderTrueFalse();
}
```

### 模块卡牌（nanite/lumen/vsm）
复制 `html/nanite/index.html` 作为模板，修改以下部分：

1. **标题**（`<title>` 和 `<header>`）
2. **题目数据**（`dragQuestions`, `singleQuestions`, `multiQuestions`, `trueFalseQuestions` 数组）
3. **总览面板统计**（更新 `allQuestions` 数组）
4. 其他代码完全复用

### 综合 Detail 面试卡牌（ue5-detail）
复制 `html/nanite/index.html` 作为模板，修改以下部分：

1. **标题**（`<title>` 和 `<header>`）
2. **移除拖拽填空标签和代码**（跨模块不适合术语填空）
3. **题目数据**（`singleQuestions`, `multiQuestions`, `trueFalseQuestions` 数组）
4. **新增追问链显示**（检查答案后显示追问列表）
5. **总览面板统计**（更新 `allQuestions` 数组）

---

## 十一、参考资源

- 已完成的模块：
  - `html/nanite/index.html` — Nanite 模块卡牌（10 题）
  - `html/lumen/index.html` — Lumen 模块卡牌（10 题）
  - `html/vsm/index.html` — VSM 模块卡牌（7 题）
  - `html/volumetric-cloud/index.html` — 体积云 Shader 卡牌（14 题）
  - `html/ue5-detail/index.html` — 综合 Detail 面试卡牌（建设中）
- 原始资料：
  - `UE5_Nanite_timlly.md` — timlly 源码分析 Part 1
  - `UE5_Lumen_timlly.md` — timlly 源码分析 Part 2
  - `UE5_Detail.md` — 完整技术详情
  - `UE5_Concept_Cards.md` — 轻量索引

---

**Skill 创建时间:** 2026-06-20  
**版本历史:**  
- v1.0 (2026-06-20): 初始版本，基于 Nanite 模块实践总结
- v1.1 (2026-06-20): 新增判断题规范、综合 Detail 面试卡牌设计、追问链机制
- v1.2 (2026-06-24): 新增随机打乱（Reshuffle）功能：打乱题目顺序 + 选项顺序，重置分数