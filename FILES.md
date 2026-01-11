# 论文阅读Agent - 项目文件说明

## 核心文件

### [main.py](main.py)
主程序文件，包含所有核心功能：

**核心类**：
- `LLMProvider` - LLM提供商抽象基类
- `OpenAIProvider` - OpenAI (GPT) 实现
- `GeminiProvider` - Google Gemini 实现
- `PDFConverter` - PDF到Markdown转换器
- `PaperAnalyzer` - 论文分析器（核心逻辑）
- `PaperReadingAgent` - 主入口类

**使用方式**：
```bash
# 命令行
python main.py paper.pdf

# Python代码
from main import PaperReadingAgent
agent = PaperReadingAgent(llm_provider="openai")
agent.process_paper("paper.pdf")
```

---

## 配置文件

### [requirements.txt](requirements.txt)
Python依赖列表。安装方式：
```bash
pip install -r requirements.txt
```

包含：
- `openai` - OpenAI API
- `google-generativeai` - Gemini API  
- `pymupdf4llm` - PDF转换
- `python-dotenv` - 环境变量管理

### [.env.example](.env.example)
环境变量配置示例。使用方式：
```bash
copy .env.example .env
# 然后编辑 .env 文件，填入你的API密钥
```

---

## 文档文件

### [README.md](README.md)
完整的项目文档，包括：
- 功能介绍
- 安装说明
- 详细使用方法
- API参考
- 常见问题

### [QUICKSTART.md](QUICKSTART.md)
快速开始指南，5步开始使用：
1. 安装依赖
2. 配置API密钥
3. 准备论文
4. 运行分析
5. 查看结果

### [TODO.md](TODO.md)
项目需求文档，说明了：
- 核心目的
- 功能需求
- 实现步骤
- 要回答的问题

---

## 辅助脚本

### [example.py](example.py)
示例脚本集合，包含：
1. 基本使用示例
2. 使用Gemini的示例
3. 分步执行示例
4. 批量处理示例
5. 查看分析问题列表

运行方式：
```bash
python example.py
```

### [check_env.py](check_env.py)
环境检查脚本，验证：
- Python版本
- 依赖包安装
- API密钥配置
- 主程序文件
- 功能测试

运行方式：
```bash
python check_env.py
```

---

## 其他文件

### [.gitignore](.gitignore)
Git忽略文件配置，排除：
- Python缓存文件
- 虚拟环境
- 环境变量文件
- 输出文件
- IDE配置

---

## 项目结构概览

```
assignment6/
├── main.py              # 主程序（核心）
├── example.py           # 示例脚本
├── check_env.py         # 环境检查
│
├── requirements.txt     # 依赖列表
├── .env.example        # 环境变量示例
├── .gitignore          # Git配置
│
├── README.md           # 完整文档
├── QUICKSTART.md       # 快速开始
├── TODO.md             # 需求文档
└── FILES.md            # 本文件
```

---

## 工作流程

```
1. 准备PDF论文
   ↓
2. 运行 main.py
   ↓
3. PDF → Markdown (使用 PDFConverter)
   ↓
4. 分析论文 (使用 PaperAnalyzer)
   - 基本信息 (3个问题)
   - 结构写作 (4个问题)
   - 图表分析 (4个问题)
   - 写作建议 (5个问题)
   - 深度思考 (5个问题)
   ↓
5. 生成Markdown报告
   ↓
6. 查看结果
```

---

## 常用命令速查

```bash
# 检查环境
python check_env.py

# 安装依赖
pip install -r requirements.txt

# 基本使用
python main.py paper.pdf

# 指定提供商
python main.py paper.pdf --provider gemini

# 指定输出目录
python main.py paper.pdf --output-dir ./output

# 查看示例
python example.py

# 查看帮助
python main.py --help
```

---

## 输出文件

运行后会生成：

1. **`{论文名}.md`** - Markdown格式的论文内容
   - 保留所有文字
   - 提取并关联图片
   - 结构清晰

2. **`{论文名}_analysis.md`** - 详细分析报告
   - 按类别组织
   - 包含所有问答
   - Markdown格式便于阅读

---

## 自定义扩展

### 添加新问题
编辑 `main.py` 中的 `PaperAnalyzer.ANALYSIS_QUESTIONS`

### 添加新LLM提供商
继承 `LLMProvider` 类并实现 `chat` 方法

### 修改输出格式
修改 `PaperAnalyzer.save_analysis_report` 方法

---

## 技术栈

- **语言**: Python 3.7+
- **LLM**: OpenAI API, Google Generative AI
- **PDF处理**: pymupdf4llm
- **架构**: 面向对象，模块化设计

---

## 支持

遇到问题？
1. 运行 `python check_env.py` 检查环境
2. 查看 [README.md](README.md) 常见问题章节
3. 查看 [QUICKSTART.md](QUICKSTART.md) 快速指南

---

**最后更新**: 2026年1月11日
