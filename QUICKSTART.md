# 快速开始指南

## 第1步：安装依赖

```bash
pip install -r requirements.txt
```

需要安装的包：
- `openai` - OpenAI API客户端
- `google-generativeai` - Google Gemini API客户端  
- `pymupdf4llm` - PDF转Markdown的高质量转换库
- `python-dotenv` - 环境变量管理（可选）

## 第2步：配置API密钥

### 选项A：使用环境变量（推荐）

1. 复制示例文件：
```bash
copy .env.example .env
```

2. 编辑 `.env` 文件，填入你的API密钥：
```
OPENAI_API_KEY=sk-your-actual-key-here
# 或
GEMINI_API_KEY=your-gemini-key-here
```

### 选项B：命令行参数

直接在命令行提供API密钥（见下方使用示例）。

## 第3步：准备论文

将你想分析的PDF论文放在项目目录中，例如 `my_paper.pdf`。

## 第4步：运行分析

### 最简单的方式（使用OpenAI）

```bash
python main.py my_paper.pdf
```

### 使用Gemini

```bash
python main.py my_paper.pdf --provider gemini
```

### 指定模型和输出目录

```bash
python main.py my_paper.pdf --provider openai --model gpt-4 --output-dir ./output
```

### 直接提供API密钥

```bash
python main.py my_paper.pdf --api-key sk-your-key-here
```

## 第5步：查看结果

程序会生成两个文件：

1. **`my_paper.md`** - PDF转换的Markdown文件
2. **`my_paper_analysis.md`** - 详细的分析报告

打开分析报告查看：
- 论文基本信息
- 结构和写作技巧
- 图表分析
- 写作建议
- 深度思考

## 更多示例

运行示例脚本查看更多用法：

```bash
python example.py
```

这会显示一个交互式菜单，包括：
1. 基本使用示例
2. 使用Gemini的示例
3. 分步执行示例
4. 批量处理多篇论文
5. 查看所有分析问题

## 编程使用

```python
from main import PaperReadingAgent

# 创建Agent
agent = PaperReadingAgent(
    llm_provider="openai",  # 或 "gemini"
    model="gpt-4"
)

# 分析论文
report = agent.process_paper("my_paper.pdf", output_dir="./output")
print(f"分析完成: {report}")
```

## 常见问题

### Q: 出现"需要提供OpenAI API密钥"错误

**A**: 确保已设置环境变量或使用 `--api-key` 参数。

### Q: 分析过程很慢

**A**: 这是正常的。完整分析包含17个问题，每个都需要LLM处理。根据论文长度，可能需要3-10分钟。

### Q: 如何节省API费用？

**A**: 
- 使用 `gpt-3.5-turbo` 而非 `gpt-4`
- 或使用 Google Gemini（通常更便宜）
- 先用短论文测试

### Q: PDF转换失败

**A**: 
- 确保PDF不是加密的
- 扫描版PDF效果较差，建议使用文字版
- 检查文件路径是否正确

### Q: 想修改分析问题

**A**: 编辑 [main.py](main.py) 中的 `PaperAnalyzer.ANALYSIS_QUESTIONS` 列表。

## 获取API密钥

### OpenAI
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新密钥

### Google Gemini
1. 访问 https://makersuite.google.com/app/apikey
2. 使用Google账号登录
3. 创建API密钥

## 下一步

- 阅读完整的 [README.md](README.md) 了解所有功能
- 查看 [main.py](main.py) 了解实现细节
- 运行 [example.py](example.py) 探索更多用法
- 根据需要自定义分析问题

---

**提示**: 第一次使用建议用较短的论文（5-10页）测试，确认一切正常后再分析长论文。
