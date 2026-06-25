# RAG 技术面试 Detail 文档

> **版本:** 1.0
> **路径:** `D:\GitRepo-My\GameDevVault\Career\Kimi\RAG\`
> **适用场景:** RAG 技术面试前 2 小时深入复习
> **原始资料:** [datawhalechina/all-in-rag](https://github.com/datawhalechina/all-in-rag)

---

## §1.1 RAG 简介与四步构建

### 核心概念
RAG（Retrieval-Augmented Generation）通过外部知识检索增强 LLM 生成能力，解决两大核心问题：
- **知识固化**: LLM 参数知识无法实时更新
- **幻觉**: 模型生成与事实不符的内容

### 最小可行系统四步流程

```python
# 源码位置: code/C1/01_langchain_example.py
# 完整流程拆解

# Step 1: 数据准备
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader("../../data/C1/markdown/easy-rl-chapter1.md")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter()
texts = text_splitter.split_documents(docs)

# Step 2: 索引构建
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}  # 归一化使余弦相似度 = 点积
)

vectorstore = InMemoryVectorStore(embeddings)
vectorstore.add_documents(texts)

# Step 3: 检索优化
retrieved_docs = vectorstore.similarity_search(question, k=3)
docs_content = "\n\".join(doc.page_content for doc in retrieved_docs)

# Step 4: 生成集成
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatOpenAI

prompt = ChatPromptTemplate.from_template("""请根据下面提供的上下文信息来回答问题。
如果上下文中没有足够的信息来回答问题，请直接告知。\n\n上下文:{context}\n\n问题:{question}\n\n回答:""")

llm = ChatOpenAI(model="glm-4.7-flash-free", temperature=0.7)
answer = llm.invoke(prompt.format(question=question, context=docs_content))
```

### 追问链

**Q: 为什么 `normalize_embeddings=True` 很重要？**
> 归一化后向量的模长为 1，此时点积（Dot Product）等价于余弦相似度（Cosine Similarity），可以简化计算并避免模长差异干扰相似度判断。FAISS 的 `IndexFlatIP`（内积）在归一化向量下等价于 cosine 搜索。

**Q: 为什么用 `"\n\n"` 而不是 `"\n"` 连接文档块？**
> 双换行符代表段落分隔，帮助 LLM 在语义上区分独立文本片段，减少信息混淆。

**Q: `temperature=0.7` 的含义？**
> Temperature 控制生成随机性。0 最确定（greedy），1 最随机。0.7 是平衡创造性和一致性的常用值。RAG 场景中通常建议 0.3-0.7，过高会导致幻觉增加。

### 判断题素材
- ❌ "RAG 完全不需要 LLM 就能回答问题" → 检索只召回上下文，答案生成仍需 LLM
- ❌ "RAG 能 100% 消除幻觉" → 只能约束，检索错误上下文或 LLM 不遵循指示时仍可能幻觉

---

## §1.2 框架对比：LangChain vs LlamaIndex

### LangChain 架构特点
- **Chain 抽象**: 将组件（Loader → Splitter → Embedding → VectorStore → LLM）串联成管道
- **Agent 能力**: 支持工具调用、多步推理
- **细粒度控制**: 每个步骤可自定义替换

### LlamaIndex 架构特点
- **Index 抽象**: `VectorStoreIndex.from_documents()` 封装了加载、分块、嵌入、存储全流程
- **Query Engine**: `index.as_query_engine()` 一行代码实现检索+生成
- **低代码**: 适合快速原型，但底层黑盒

### 选择建议
| 场景 | 推荐框架 |
|------|----------|
| 快速原型/MVP | LlamaIndex |
| 深度定制/生产级 | LangChain |
| 需要 Agent 多步推理 | LangChain |
| 复杂索引结构（图、树） | LlamaIndex |

### 追问链
**Q: LlamaIndex 的 `Settings.llm` 和 `Settings.embed_model` 是全局单例吗？**
> 是的，LlamaIndex 使用全局 Settings 对象管理默认 LLM 和嵌入模型，所有 Index 和 QueryEngine 默认使用这些配置。可以通过参数覆盖单个组件的配置。

---

## §2.1 文本分块：为什么 Chunk 不是越大越好

### 信息损失机制

Transformer 编码器的工作流程：
1. **分词** → Tokenization
2. **向量化** → 每个 token 生成高维向量
3. **池化** → `[CLS]` 或 mean pooling 压缩成单一向量

```python
# 源码位置: langchain_text_splitters/character.py
# CharacterTextSplitter._merge_splits 核心逻辑

def _merge_splits(self, splits, separator):
    """将分割后的片段合并成块"""
    docs = []
    current_doc = []
    total = 0
    for d in splits:
        _len = self._length_function(d)
        if total + _len + (len(separator) if current_doc else 0) > self._chunk_size:
            if total > self._chunk_size:
                logger.warning(f"Created a chunk of size {total}, which is longer than {self._chunk_size}")
            if current_doc:
                docs.append(self._join_docs(current_doc, separator))
            # 保留重叠部分
            while total > self._chunk_overlap or (
                total + _len + (len(separator) if current_doc else 0) > self._chunk_size and total > 0
            ):
                total -= self._length_function(current_doc[0]) + (len(separator) if len(current_doc) > 1 else 0)
                current_doc = current_doc[1:]
        current_doc.append(d)
        total += _len + (len(separator) if current_doc else 0)
    if current_doc:
        docs.append(self._join_docs(current_doc, separator))
    return docs
```

### "Lost in the Middle" 效应

> [Liu et al. (2023)](https://arxiv.org/abs/2307.03172) 发现：LLM 处理长上下文时，对开头和结尾的信息记忆更好，中间部分容易被忽略。

**影响**: 如果 chunk 过大且包含多个主题，关键信息可能被淹没在无关内容中。

### 追问链
**Q: chunk_size=4000, chunk_overlap=200 的实际含义？**
> chunk_size 是目标块大小（以 token 或字符计，取决于 splitter），overlap 是相邻块之间的重叠量。overlap 的作用是保持上下文连续性，避免在边界处语义断裂。但 overlap 过大（>25%）会导致冗余增加、存储成本上升、检索多样性下降。

**Q: 如果单个段落超过 chunk_size 怎么办？**
> `CharacterTextSplitter` 会发出警告但保留整个段落；`RecursiveCharacterTextSplitter` 会继续用更细粒度分隔符（句子→单词→字符）递归切分，直到满足大小要求。

---

## §2.2 RecursiveCharacterTextSplitter 算法详解

### 算法流程

```python
# 源码位置: langchain_text_splitters/character.py
# RecursiveCharacterTextSplitter._split_text 核心逻辑

def _split_text(self, text, separators):
    """递归分割文本"""
    # 1. 找到第一个存在的分隔符
    separator = separators[-1]  # 默认最后一个（空字符串）
    for s in separators:
        if s == "" or s in text:
            separator = s
            break
    
    # 2. 用分隔符切分
    splits = self._split_text_with_regex(text, separator, self._keep_separator)
    
    # 3. 分类处理
    _good_splits = []
    for s in splits:
        if self._length_function(s) < self._chunk_size:
            _good_splits.append(s)  # 合格片段，暂存
        else:
            if _good_splits:
                merged_text = self._merge_splits(_good_splits, separator)
                final_chunks.extend(merged_text)
                _good_splits = []
            
            # 超长片段：递归处理
            if not new_separators:  # 分隔符用尽
                final_chunks.append(s)  # 直接保留
            else:
                other_info = self._split_text(s, new_separators)  # 递归
                final_chunks.extend(other_info)
    
    # 4. 处理剩余合格片段
    if _good_splits:
        merged_text = self._merge_splits(_good_splits, separator)
        final_chunks.extend(merged_text)
    
    return final_chunks
```

### 关键设计
- **批处理机制**: 先收集所有合格片段（`_good_splits`），遇到超长片段时才触发合并，减少不必要的合并操作
- **递归终止条件**: `if not new_separators` 确保不会无限递归
- **默认分隔符**: `["\n\n", "\n", " ", ""]` — 按语义层级从高到低

### 中文优化分隔符
```python
separators=[
    "\n\n", "\n", " ",  # 标准分隔符
    "。", "，",           # 中文句号、逗号
    "\u200b",            # 零宽空格（泰文、日文）
    "\uff0c", "\u3001",   # 全角逗号、顿号
    "\uff0e", "\u3002",   # 全角句号
    ""
]
```

### 追问链
**Q: 为什么 `_good_splits` 是批处理而不是逐个合并？**
> 如果逐个合并，每个合格片段都会触发一次 `_merge_splits`，而 `_merge_splits` 需要检查累积长度是否超过 chunk_size。批处理将所有小片段收集后一次性合并，减少了边界检查次数，提升效率。

**Q: 编程语言特化的 `from_language` 有什么优势？**
> 针对 Python 等语言使用类定义、函数定义、控制流语句等作为分隔符，确保不会在代码逻辑中间切断，比纯文本分隔符更符合代码结构。

---

## §2.3 语义分块（Semantic Chunking）实现原理

### 完整流程

```python
# 源码位置: langchain_experimental/text_splitter.py
# SemanticChunker 核心逻辑

class SemanticChunker:
    def split_documents(self, documents):
        # 1. 句子分割
        sentences = self._split_sentences(documents)
        
        # 2. 上下文感知嵌入（buffer_size=1）
        # 每个句子与前后各1句组合后嵌入
        combined_sentences = []
        for i in range(len(sentences)):
            start = max(0, i - self.buffer_size)
            end = min(len(sentences), i + self.buffer_size + 1)
            combined = " ".join(sentences[start:end])
            combined_sentences.append(combined)
        
        embeddings = self.embeddings.embed_documents(combined_sentences)
        
        # 3. 计算相邻句子语义距离
        distances = []
        for i in range(len(embeddings) - 1):
            distance = cosine_distance(embeddings[i], embeddings[i+1])
            distances.append(distance)
        
        # 4. 识别断点（百分位法/标准差法/四分位距法/梯度法）
        if self.breakpoint_threshold_type == "percentile":
            threshold = np.percentile(distances, self.breakpoint_threshold_amount)
        elif self.breakpoint_threshold_type == "standard_deviation":
            threshold = np.mean(distances) + self.breakpoint_threshold_amount * np.std(distances)
        elif self.breakpoint_threshold_type == "interquartile":
            q1, q3 = np.percentile(distances, [25, 75])
            iqr = q3 - q1
            threshold = q3 + self.breakpoint_threshold_amount * iqr
        elif self.breakpoint_threshold_type == "gradient":
            # 计算距离变化率，再用百分位法
            gradients = np.gradient(distances)
            threshold = np.percentile(gradients, self.breakpoint_threshold_amount)
        
        # 5. 在断点处切分
        chunks = []
        current_chunk = [sentences[0]]
        for i, distance in enumerate(distances):
            if distance > threshold:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i+1]]
            else:
                current_chunk.append(sentences[i+1])
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
```

### 断点识别方法对比

| 方法 | 逻辑 | 适用场景 |
|------|------|----------|
| **percentile** | 第 N 百分位作为阈值 | 通用场景，默认推荐 |
| **standard_deviation** | 均值 + N * 标准差 | 距离分布较均匀时 |
| **interquartile** | Q3 + N * IQR | 存在异常值时更稳健 |
| **gradient** | 距离变化率 + 百分位 | 语义联系紧密的文档（法律、医疗） |

### 追问链
**Q: `buffer_size` 的作用是什么？如果设为 0 会怎样？**
> `buffer_size` 决定每个句子嵌入时包含多少上下文。设为 1 表示每个句子与前后各 1 句组合后嵌入，使嵌入向量融入上下文语义。如果设为 0，每个句子独立嵌入，失去上下文信息，可能误判语义跳跃。

**Q: 语义分块的计算成本为什么比递归字符分块高？**
> 每个句子需要一次嵌入模型调用（或批量调用），如果文档有 100 个句子，需要 100 次嵌入计算。而递归字符分块只需要字符串操作，无模型推理。

---

## §2.4 MarkdownHeaderTextSplitter 与组合策略

### 实现原理
```python
# 先按标题分组，保留标题元数据
headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_chunks = splitter.split_text(markdown_text)

# 再用 RecursiveCharacterTextSplitter 细分，元数据继承
recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
final_chunks = recursive_splitter.split_documents(md_chunks)
# 每个 final_chunk 保留 Header 1 和 Header 2 的元数据
```

### 元数据注入的价值
```python
# 元数据示例
{
    "Header 1": "第三章：模型评估",
    "Header 2": "3.2节：评估指标"
}
```
LLM 在生成时可以理解信息来源和层级关系，提升回答准确性。

---

## §3.1 向量嵌入技术演进

### 静态词嵌入 → 动态上下文嵌入

| 阶段 | 代表模型 | 原理 | 局限 |
|------|----------|------|------|
| 静态词嵌入 | Word2Vec, GloVe | 每个词固定向量 | 一词多义 |
| 动态上下文 | BERT, RoBERTa | 自注意力动态编码 | 计算成本高 |
| 检索特化 | SBERT, BGE, E5 | 对比学习/度量学习 | 领域迁移需微调 |

### BERT 训练任务详解

**MLM（掩码语言模型）**
- 随机遮盖 15% 的 token（80% 替换为 [MASK]，10% 随机词，10% 保持原词）
- 目标：预测被遮盖的原始 token
- 为什么 15%？遮盖太少 → 训练效率低；遮盖太多 → 上下文信息不足

**NSP（下一句预测）→ 已弃用**
- RoBERTa 论文发现：NSP 过于简单（模型只需判断两个话题是否一致，无需真正理解句子关系），甚至损害下游任务性能
- 现代模型（RoBERTa, DeBERTa, ALBERT）已移除 NSP

### 追问链
**Q: BERT 的 `[CLS]` 和 `[SEP]` 分别是什么？**
> `[CLS]` 是分类标记，位于输入开头，通过自注意力聚合全局信息，最终向量代表整个序列的语义；`[SEP]` 是分隔标记，用于分隔句子对（如 QA 中的问题和答案）。在嵌入场景中，通常使用 `[CLS]` 或 mean pooling 作为句子表示。

**Q: 为什么对比学习要优化"相对距离"而非绝对相似度？**
> 如果追求绝对相似度（正例对必须接近 1.0），模型可能过拟合到训练数据的特定分布，泛化能力下降。相对距离优化（正例比负例更近）让模型学习更鲁棒的排序关系。

---

## §3.2 Embedding 模型选型与 MTEB

### MTEB 四维度评估

```
横轴：模型参数量（能力 vs 资源）
纵轴：平均任务得分（通用语义能力）
气泡大小：嵌入维度（信息密度 vs 存储成本）
气泡颜色：最大处理长度（长文本适应性）
```

### 选型决策树
1. **语言**: 中文优先选 BGE 系列、Jina v3
2. **任务**: RAG 重点看 Retrieval 排名
3. **规模**: 生产环境权衡 latency 和 accuracy
4. **领域**: 通用领域用 BGE-M3，专业领域考虑微调

### 迭代测试流程
```
选基线模型 → 构建私有评测集（问题+标准答案）
    → 运行评估 → 分析 bad case → 调整策略（换模型/改分块/改检索参数）
    → 迭代优化 → 选定最终模型
```

---

## §3.3 向量数据库工作原理

### 四层架构

```
存储层 → 索引层 → 查询层 → 服务层
  ↓        ↓        ↓        ↓
向量存储  HNSW/IVF  混合查询  客户端连接
元数据    索引创建  查询优化  监控日志
分布式    索引调整  范围查询  安全管理
```

### 核心索引算法对比

| 算法 | 类型 | 原理 | 适用场景 |
|------|------|------|----------|
| **HNSW** | 图 | 分层可导航小世界图，多层邻近结构 | 高召回、高维度 |
| **IVF** | 量化 | 先聚类再搜索，减少比较次数 | 大规模数据 |
| **LSH** | 哈希 | 局部敏感哈希，相似向量映射到同一桶 | 低精度快速检索 |
| **PQ** | 量化 | 乘积量化，压缩向量减少存储 | 内存受限场景 |
| **Flat** | 暴力 | 线性扫描，精确计算 | 小规模、高精度 |

### HNSW 核心参数
- `M`: 每个节点的最大邻居数（默认 16），越大图越稠密，召回越高，但构建和内存开销增加
- `ef_construction`: 构建时的搜索深度（默认 100），越大图质量越好，构建越慢
- `ef_search`: 查询时的搜索深度（默认 100），越大召回越高，查询越慢

### 追问链
**Q: HNSW 的 "可导航小世界" 是什么意思？**
> 小世界网络特性：任意两点间存在短路径（六度分隔理论）。HNSW 构建多层图，底层是精细连接，上层是稀疏"高速公路"，查询时从上层快速定位到大致区域，再到底层精确搜索，实现对数复杂度。

**Q: 为什么向量数据库通常使用最终一致性而非强一致性？**
> 向量检索的核心是近似最近邻（ANN），本身就允许微小误差。强一致性（如分布式事务）会带来巨大性能开销，与 ANN 的"近似"理念冲突。对于实时性要求高的场景，通常采用异步索引更新 + 最终一致性。

---

## §3.4 FAISS 索引创建流程（LangChain 源码级）

```python
# 源码层级拆解

# Layer 1: 封装层
FAISS.from_documents(docs, embeddings)
  └─> 提取 page_content 和 metadata
  └─> 调用 from_texts(texts, embeddings, metadatas)

# Layer 2: 向量化入口
FAISS.from_texts(texts, embeddings, metadatas)
  └─> embeddings.embed_documents(texts)  # 批量嵌入
  └─> 调用 __from(texts, embeddings_list, metadatas)

# Layer 3: 构建空框架
FAISS.__from(texts, embeddings, metadatas)
  └─> 初始化 IndexFlatL2（默认 L2 距离）
  └─> 准备 docstore（文档存储）
  └─> 准备 index_to_docstore_id（ID 映射）
  └─> 调用 __add(texts, embeddings, metadatas)

# Layer 4: 填充数据
FAISS.__add(texts, embeddings, metadatas)
  └─> index.add(np.array(embeddings))  # 添加向量到 FAISS
  └─> docstore.mset({doc_id: Document(...)})  # 存储原文档
  └─> 更新 index_to_docstore_id 映射
```

### 距离度量选择
- **L2 (欧氏距离)**: 默认，适合归一化后的向量空间
- **IP (内积)**: 归一化向量下等价于 cosine，计算更快
- **Cosine**: 直接计算夹角余弦，语义相似度最常用

---

## §3.5 Milvus 混合检索实现

### Schema 设计
```python
fields = [
    FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=True),
    FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
    FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=1024)
]
```

### BGE-M3 双向量生成
```python
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

ef = BGEM3EmbeddingFunction(use_fp16=False, device="cpu")
embeddings = ef(docs)
sparse_vectors = embeddings["sparse"]   # 稀疏：关键词权重，维度 ~250k
dense_vectors = embeddings["dense"]     # 密集：语义编码，维度 1024
```

### 混合检索执行
```python
# 创建 RRF 融合器
rerank = RRFRanker(k=60)

# 创建搜索请求
dense_req = AnnSearchRequest([dense_vec], "dense_vector", search_params, limit=top_k)
sparse_req = AnnSearchRequest([sparse_vec], "sparse_vector", search_params, limit=top_k)

# 执行混合搜索
results = collection.hybrid_search(
    [sparse_req, dense_req],
    rerank=rerank,
    limit=top_k
)
```

### 追问链
**Q: 为什么混合检索中 "驯龙高手" 从第 3 降到第 5？**
> 密集检索中排第 3，稀疏检索中也排第 3。RRF 公式：score = 1/(3+60) + 1/(3+60) ≈ 0.032。其他文档虽然在单个检索器中排名不同，但 RRF 融合后总分可能更高。RRF 的设计使得在多个检索器中都排中等的文档，可能超过在单个检索器中排名高但另一检索器中排名低的文档。

**Q: `k=60` 的 RRF 参数有什么影响？**
> k 是平滑常数。k 越大，排名差异的影响越平滑（高排名和低排名的分数差距被缩小）；k 越小，高排名结果的权重越突出。k=60 是论文推荐值，在多样性和精确性之间取得平衡。

---

## §4.1 混合检索融合策略

### RRF vs 加权线性组合

| 特性 | RRF | 加权线性组合 |
|------|-----|-------------|
| 是否需要归一化 | 否 | 是（必须统一分数尺度） |
| 是否关心绝对分数 | 否 | 是 |
| 参数复杂度 | 低（仅 k） | 高（α + 归一化方法） |
| 鲁棒性 | 高（对异常分数不敏感） | 中（依赖归一化质量） |
| 适用场景 | 通用、多路召回 | 已知语义/关键词权重偏好 |

### 加权融合公式
$$ Hybrid_{score} = \alpha \cdot Dense_{score} + (1 - \alpha) \cdot Sparse_{score} $$

- α = 0.7: 偏重语义理解（智能问答）
- α = 0.3: 偏重关键词匹配（电商搜索、产品型号）

---

## §4.2 重排序（Re-ranking）技术对比

### 四种重排方法

| 方法 | 核心机制 | 计算成本 | 交互粒度 | 适用场景 |
|------|----------|----------|----------|----------|
| **RRF** | 融合多个排名 | 低（数学计算） | 无 | 多路召回融合 |
| **RankLLM** | LLM 推理生成排序 | 中（API 费用） | 概念/语义级 | 高价值语义场景 |
| **Cross-Encoder** | 查询-文档联合编码 | 高（N次推理） | 句子级 | Top-K 精排 |
| **ColBERT** | 独立编码 + 后期交互 | 中（向量点积） | Token 级 | Top-K 重排 |

### Cross-Encoder 工作流程
```python
# 输入: [CLS] query [SEP] document [SEP]
# 输出: 单一相关性分数 (0~1)

for doc in candidate_docs:
    pair = f"[CLS] {query} [SEP] {doc} [SEP]"
    score = cross_encoder_model(pair)  # 一次完整推理
    scores.append(score)

# 按分数重排序
reranked = sorted(zip(candidate_docs, scores), key=lambda x: x[1], reverse=True)
```

### ColBERT MaxSim 操作详解
```python
# 1. 独立编码（可预先计算文档向量）
q_emb = model.encode(query)    # [query_len, dim]
d_emb = model.encode(document) # [doc_len, dim]

# 2. 计算相似度矩阵
sim_matrix = q_emb @ d_emb.T   # [query_len, doc_len]

# 3. MaxSim: 每个查询 token 找文档中最相似 token
max_sim_per_q_token = sim_matrix.max(dim=1).values  # [query_len]

# 4. 聚合：求和得到最终分数
colbert_score = max_sim_per_q_token.sum()
```

### 追问链
**Q: 为什么 Cross-Encoder 精度高但延迟大？**
> Cross-Encoder 将查询和文档拼接后输入 Transformer，自注意力机制允许查询 token 和文档 token 直接交互，捕获细粒度语义关系。但每次评分需要一次完整的模型前向传播，对 50 个候选文档需要 50 次推理。Bi-Encoder 只需 1 次查询编码 + 向量点积（可预先计算文档向量）。

**Q: ColBERT 为什么说在精度和效率间取得平衡？**
> 文档编码可离线预先计算和存储（像 Bi-Encoder），查询时只需计算 MaxSim 和求和（比 Cross-Encoder 的完整 Transformer 推理快得多），同时保留了 token 级交互能力（比 Bi-Encoder 的单一 `[CLS]` 向量更精细）。

---

## §4.3 上下文压缩与 DocumentCompressorPipeline

### LangChain 压缩器类型

```python
# 1. LLMChainExtractor: 内容提取
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
# 遍历每个文档，用 LLM 提取与查询相关的部分

# 2. LLMChainFilter: 文档过滤
from langchain.retrievers.document_compressors import LLMChainFilter

filter = LLMChainFilter.from_llm(llm)
# 判断整个文档是否相关，不相关则直接丢弃

# 3. EmbeddingsFilter: 快速相似度过滤
from langchain.retrievers.document_compressors import EmbeddingsFilter

embeddings_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.6)
# 计算查询与文档的嵌入相似度，低于阈值丢弃
```

### 自定义 ColBERT 重排器
```python
from langchain.schema import BaseDocumentCompressor
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

class ColBERTReranker(BaseDocumentCompressor):
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def compress_documents(self, documents, query, callbacks=None):
        # 编码查询和文档
        q_inputs = self.tokenizer([query], return_tensors="pt", padding=True, truncation=True)
        doc_texts = [doc.page_content for doc in documents]
        d_inputs = self.tokenizer(doc_texts, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            q_outputs = self.model(**q_inputs)
            d_outputs = self.model(**d_inputs)
            q_emb = F.normalize(q_outputs.last_hidden_state, p=2, dim=-1)
            d_emb = F.normalize(d_outputs.last_hidden_state, p=2, dim=-1)
        
        # ColBERT MaxSim
        scores = []
        for i in range(len(documents)):
            doc_i = d_emb[i].unsqueeze(0)  # [1, doc_len, dim]
            sim = torch.matmul(q_emb, doc_i.transpose(-2, -1))  # [1, q_len, doc_len]
            max_sim = sim.max(dim=-1)[0]  # [1, q_len]
            score = max_sim.sum().item()
            scores.append(score)
        
        # 排序返回 Top 5
        scored = list(zip(documents, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:5]]
```

### 追问链
**Q: `DocumentCompressorPipeline` 中的 transformers 执行顺序是什么？**
> 按列表顺序依次执行。例如 `[reranker, compressor]` 表示先 ColBERT 重排，再 LLM 压缩。前一个的输出作为后一个的输入。顺序很重要：先重排再压缩，避免压缩后丢失用于重排的信息。

---

## §4.4 C-RAG（Corrective RAG）架构

### 工作流程
```
检索 (Retrieve)
    ↓
评估 (Assess) ← Retrieval Evaluator 判断文档质量
    ↓
    ├─ 正确 → 知识精炼 (Knowledge Refinement) → 分解为 strips → 过滤重组 → 生成
    ├─ 不正确 → 查询重写 → Web 搜索 → 外部知识获取 → 生成
    └─ 模糊 → Web 搜索 → 辅助信息 → 生成
```

### LangGraph 实现思路
```python
# 状态图定义
from langgraph.graph import StateGraph

graph = StateGraph()
graph.add_node("retrieve", retrieve_node)
graph.add_node("evaluate", evaluate_node)
graph.add_node("refine", refine_node)
graph.add_node("search", search_node)
graph.add_node("generate", generate_node)

graph.add_edge("retrieve", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    lambda state: state["grade"],  # "correct" / "incorrect" / "ambiguous"
    {
        "correct": "refine",
        "incorrect": "search",
        "ambiguous": "search"
    }
)
graph.add_edge("refine", "generate")
graph.add_edge("search", "generate")
```

### 追问链
**Q: C-RAG 的 "Retrieval Evaluator" 如何实现？**
> 可以用 LLM 作为评估器，设计提示词让模型判断每个文档与查询的相关性（正确/不正确/模糊）。也可以用轻量级分类器（如 BERT）微调一个三分类模型，降低评估成本。

---

## §5.1 RAG Triad 评估体系

### 三个维度详解

```mermaid
graph LR
    A[用户查询] --> B[检索器 Retriever]
    B --> C[检索到的上下文]
    C --> D[LLM 生成器]
    D --> E[最终答案]
    
    style B fill:#e8f5e9
    style D fill:#e8f5e9
    style E fill:#e8f5e9
```

| 维度 | 评估目标 | 核心问题 | 低分原因 |
|------|----------|----------|----------|
| **上下文相关性** | 检索器 | 检索内容与查询相关吗？ | 分块不当、嵌入模型差、检索 k 太小 |
| **忠实度** | 生成器 | 答案基于上下文吗？ | LLM 不遵循指示、提示词设计缺陷 |
| **答案相关性** | 端到端 | 答案完整回答问题吗？ | 检索缺失、LLM 理解偏差、生成不完整 |

### 追问链
**Q: 忠实度低但答案相关性高，可能是什么原因？**
> LLM 引入了外部知识（参数知识）来回答问题，虽然答案本身很好，但没有严格基于检索到的上下文。这会导致无法溯源验证，在需要严格事实依据的场景很危险。

**Q: 上下文相关性高但忠实度低，可能是什么原因？**
> 检索到了正确的文档，但 LLM 没有基于这些文档回答，可能：① 提示词没有明确约束"只能基于上下文"；② 上下文与 LLM 的参数知识冲突，模型选择了"更熟悉"的参数知识；③ 上下文格式混乱，LLM 无法有效利用。

---

## §5.2 检索评估指标

### Precision@k, Recall@k, F1
```
Precision@k = 检索到的前 k 个结果中的相关文档数 / k
Recall@k = 检索到的前 k 个结果中的相关文档数 / 所有真实相关文档总数
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

### MRR（平均倒数排名）
```
MRR = (1/|Q|) * Σ(1 / rank_q)
```
- 只关注第一个相关文档的排名位置
- 适用于用户通常只看第一个结果的场景

### MAP（平均准确率均值）
```
MAP = (1/|Q|) * Σ(AP(q))
AP(q) = Σ(Precision@k * rel(k)) / 相关文档总数
```
- 同时考虑精确率和文档排名
- 每出现一个相关文档，计算该位置的精确率，再取平均

---

## §5.3 生成评估指标

### ROUGE（召回率导向）
```
ROUGE-N = 匹配的 n-gram 数量 / 参考答案中 n-gram 的总数
```
- 关注"说全了没"：参考答案中的内容有多少被生成答案覆盖
- 常用 ROUGE-1（unigram）、ROUGE-2（bigram）、ROUGE-L（最长公共子序列）

### BLEU（精确率导向）
```
BLEU = BP * exp(Σ(w_n * log(p_n)))
BP = 1                          if c > r
BP = e^(1 - r/c)                if c <= r   (长度惩罚)
```
- 关注"说对了没"：生成答案中有多少词在参考答案中出现过
- 引入 Brevity Penalty（长度惩罚）避免生成过短答案

### METEOR（综合平衡）
```
F_mean = (P * R) / (α*P + (1-α)*R)
METEOR = F_mean * (1 - Penalty)
```
- 同时计算精确率 P 和召回率 R 的调和平均
- 通过词干和同义词匹配捕捉语义相似性（如 boat 和 ship）
- Penalty 是基于语序的惩罚项

### 三指标对比示例
```
参考答案: "狗 在 床 上面"
生成答案: "狗 在 床 上"

ROUGE-1: 4/5 = 0.8   (召回率高，说全了)
BLEU:   ~0.6          (精确率高但长度惩罚扣分)
METEOR: ~0.75         (平衡，考虑同义词和语序)
```

---

## §5.4 基于 LLM 的评估方法

### 忠实度评估流程
```python
# 1. 分解答案为独立声明（Claims）
claims = llm_extract_claims(answer)
# 例如: ["法国在西欧", "法国首都是巴黎"]

# 2. 每个声明在上下文中验证
verified = []
for claim in claims:
    is_supported = llm_verify(claim, context)
    verified.append(is_supported)

# 3. 忠实度 = 被证实的声明比例
faithfulness = sum(verified) / len(verified)
```

### 答案相关性评估
```python
# 评估者分析查询和答案的匹配度
score = llm_evaluate_relevance(query, answer)
# 惩罚：答非所问、信息不完整、包含无关细节
```

### 方法对比总结
| 方法 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| **LLM 评估** | 语义理解深、逻辑判断强 | 成本高、有评估者偏见 | 精细评估、边界案例 |
| **词汇重叠** | 客观、快速、成本低 | 无法理解语义、误判同义词 | 大规模批量筛选 |

**最佳实践**: 先用词汇重叠指标快速筛选，再用 LLM 对关键案例精细评估。

---

## §6.1 知识图谱 RAG 与 Graph RAG

### 知识图谱 vs 向量检索

| 维度 | 向量 RAG | 知识图谱 RAG |
|------|----------|-------------|
| 数据结构 | 无结构向量 | 实体-关系-属性图 |
| 推理能力 | 语义相似匹配 | 多跳推理、路径遍历 |
| 可解释性 | 低（黑盒相似度） | 高（关系路径可追溯） |
| 构建成本 | 低（自动嵌入） | 高（需实体抽取、关系识别） |
| 适合问题 | "什么是 XXX" | "XXX 和 YYY 的关系是什么" |

### Graph RAG 架构（C9 项目）
```
图数据建模（Entity-Relation-Attribute）
    ↓
图数据准备（抽取 → 存储到 Neo4j）
    ↓
Milvus 索引构建（向量 + 图索引）
    ↓
智能查询路由（向量检索 / 图遍历 / 混合）
```

### 追问链
**Q: Graph RAG 中向量检索和图遍历如何互补？**
> 向量检索适合"概念匹配"（找到与查询语义相似的实体）；图遍历适合"关系推理"（从已知实体出发，沿着关系路径找到关联信息）。混合策略：先用向量检索定位相关实体，再用图遍历扩展关系网络。

---

## 附录：性能优化与面试追问清单

### 常见追问类型速查

| 追问类型 | 示例 | 回答要点 |
|----------|------|----------|
| **Why?** | 为什么 RAG 比微调更适合频繁更新的知识库？ | 微调需要重新训练，RAG 只需更新向量库 |
| **How?** | 如何实现检索结果的实时更新？ | 增量嵌入 + 异步索引重建 + 双 buffer 切换 |
| **What if?** | 如果嵌入模型和 LLM 语言不一致怎么办？ | 使用多语言嵌入模型，或统一翻译管道 |
| **Compare?** | 对比 RRF 和加权融合的适用场景？ | RRF 通用鲁棒，加权融合需要已知偏好 |
| **Future?** | RAG 的未来发展方向？ | Agentic RAG、多模态 RAG、自适应分块 |
| **Interview?** | 如果面试官问 RAG 的延迟优化？ | 两阶段检索、缓存、预加载、索引分区 |
| **Debug?** | RAG 回答突然变差怎么排查？ | 按 RAG Triad 三步定位，检查数据源更新 |

### 生产环境 checklist
- [ ] 嵌入模型是否支持业务语言？
- [ ] 分块策略是否适合文档类型？
- [ ] 向量索引是否支持增量更新？
- [ ] 检索 k 值是否经过调优？
- [ ] 是否有重排序提升精度？
- [ ] 上下文压缩是否启用？
- [ ] 评估体系是否建立？
- [ ] 是否有 fallback 机制（Web 搜索）？

---

**创建时间:** 2025-06-25
**版本历史:**
- v1.0 (2025-06-25): 初始版本，覆盖 all-in-rag 核心章节源码级解析
