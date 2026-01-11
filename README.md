# 论文阅读Agent

一个专门用于阅读和分析学术论文的AI Agent，帮助学习论文写作技巧。

## 功能特点

✨ **多LLM支持**: 支持OpenAI (GPT-4) 和 Google Gemini，可自由切换  
📄 **PDF转换**: 无损将PDF论文转换为Markdown格式，保留所有文字和图片  
🔍 **深度分析**: 从多个维度分析论文（基本信息、结构、图表、写作技巧等）  
📝 **自动报告**: 生成详细的Markdown格式分析报告  
🚀 **批量处理**: 自动处理papers文件夹中的所有论文（新功能！）

## 快速开始（3步）⚡

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
复制 `.env.example` 为 `.env`，填入你的API密钥

### 3. 批量处理论文
```bash
# 将PDF论文放入 papers/ 文件夹
# 运行程序
python main.py

# 查看结果：output/ 文件夹
```

**就这么简单！** 🎉

详细使用指南：[BATCH_GUIDE.md](BATCH_GUIDE.md)

---

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

有两种方式配置API密钥：

**方式1: 环境变量**

创建 `.env` 文件：
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# 或者 Gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

**方式2: 命令行参数**

使用 `--api-key` 参数直接提供。

## 使用方法

### 批量处理模式（推荐）🔥

**最简单的使用方式**：

```bash
# 1. 将PDF论文放入 papers/ 文件夹
# 2. 运行程序
python main.py

# 使用Gemini
python main.py --provider gemini

# 指定不同的文件夹
python main.py --papers-dir ./my_papers --output-dir ./my_output
```

程序会自动处理 `papers/` 文件夹中的所有PDF文件，结果保存到 `output/` 文件夹。

详细说明：[BATCH_GUIDE.md](BATCH_GUIDE.md)

### 单文件处理模式

如果只想处理一篇论文：

```bash
# 处理单个文件
python main.py --single paper.pdf

# 使用Gemini
python main.py --single paper.pdf --provider gemini

# 指定输出目录
python main.py --single paper.pdf --output-dir ./output
```

# 直接提供API密钥
python main.py paper.pdf --api-key your_api_key_here
```

### 编程使用

```python
from main import PaperReadingAgent

# 初始化Agent
agent = PaperReadingAgent(
    llm_provider="openai",  # 或 "gemini"
    api_key="your_api_key",
    model="gpt-4"  # 可选
)

# 处理论文
report_path = agent.process_paper(
    pdf_path="paper.pdf",
    output_dir="./output"  # 可选
)

print(f"分析报告: {report_path}")
```

## 分析内容

Agent会从以下5个维度分析论文：

### 1. 基本信息
- 发表平台和权威性
- 研究领域和方向
- 主要创新点

### 2. 论文结构与写作
- 研究工作的各个方面
- 内容组织和逻辑关联
- 章节安排和过渡
- 摘要和结论的呼应

### 3. 图表分析
- 所有图表的内容和作用
- 图表与文字的关联
- 核心贡献的可视化
- 图表设计特点

### 4. 写作建议
- 如何组织类似论文的结构
- 内容详略安排
- 图表设计建议
- 语言表达特点
- 值得学习的地方

### 5. 深度思考
- 核心问题和重要性
- 方法论的独特性
- 实验设计和验证
- 局限性和未来方向
- 对自己研究的启发

## 输出文件

处理完成后会生成两个文件：

1. **`{论文名}.md`**: PDF转换的Markdown文件
2. **`{论文名}_analysis.md`**: 详细的分析报告

## 项目结构

```
.
├── main.py              # 主程序
├── requirements.txt     # 依赖列表
├── README.md           # 本文档
├── .env.example        # 环境变量示例
└── TODO.md             # 项目需求文档
```

## 技术栈

- **LLM接口**: OpenAI API, Google Generative AI
- **PDF处理**: pymupdf4llm (高质量转换，保留图片)
- **Python**: 3.7+

## 注意事项

⚠️ **API费用**: 使用OpenAI或Gemini会产生API调用费用，建议：
- 先用较短的论文测试
- 选择性分析某些问题
- 使用成本较低的模型（如gpt-3.5-turbo）

⚠️ **处理时间**: 完整分析一篇论文可能需要几分钟，取决于：
- 论文长度
- LLM模型速度
- 网络连接

⚠️ **PDF质量**: 转换效果取决于PDF质量：
- 扫描版PDF效果可能较差
- 建议使用文字版PDF
- 图片会被提取并关联

## 自定义

### 修改分析问题

编辑 [main.py](main.py) 中的 `PaperAnalyzer.ANALYSIS_QUESTIONS` 可以自定义问题列表。

### 添加新的LLM提供商

继承 `LLMProvider` 类并实现 `chat` 方法：

```python
class CustomLLMProvider(LLMProvider):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # 实现你的LLM调用逻辑
        pass
```

## 常见问题

**Q: 为什么要转换为Markdown？**
A: Markdown格式结构清晰，LLM更容易理解，同时保留了图片和格式信息。

**Q: 支持中文论文吗？**
A: 支持。程序会自动处理中英文论文。

**Q: 可以批量处理多篇论文吗？**
A: 当前版本每次处理一篇，可以编写脚本循环调用。

**Q: API密钥安全吗？**
A: 建议使用环境变量而非硬编码。不要将 `.env` 文件提交到版本控制。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

**作者**: 为学习论文写作而创建
**日期**: 2026年1月
