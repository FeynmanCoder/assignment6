"""
示例脚本 - 演示如何使用论文阅读Agent
"""

from main import PaperReadingAgent
from pathlib import Path


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 创建Agent（使用OpenAI）
    agent = PaperReadingAgent(
        llm_provider="openai",
        model="gpt-4"  # 或 "gpt-3.5-turbo" 以节省成本
    )
    
    # 处理论文
    pdf_path = "your_paper.pdf"  # 替换为实际的PDF路径
    
    if Path(pdf_path).exists():
        report_path = agent.process_paper(pdf_path)
        print(f"\n✅ 完成！分析报告保存在: {report_path}")
    else:
        print(f"❌ PDF文件不存在: {pdf_path}")


def example_gemini_usage():
    """使用Gemini的示例"""
    print("=" * 60)
    print("示例2: 使用Gemini")
    print("=" * 60)
    
    # 创建Agent（使用Gemini）
    agent = PaperReadingAgent(
        llm_provider="gemini",
        model="gemini-pro"
    )
    
    # 处理论文
    pdf_path = "your_paper.pdf"
    output_dir = "./output"  # 指定输出目录
    
    if Path(pdf_path).exists():
        report_path = agent.process_paper(pdf_path, output_dir)
        print(f"\n✅ 完成！分析报告保存在: {report_path}")
    else:
        print(f"❌ PDF文件不存在: {pdf_path}")


def example_custom_analysis():
    """自定义分析示例"""
    print("=" * 60)
    print("示例3: 分步执行")
    print("=" * 60)
    
    from main import PDFConverter, PaperAnalyzer, OpenAIProvider
    
    # 第1步：转换PDF
    converter = PDFConverter()
    pdf_path = "your_paper.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print("转换PDF到Markdown...")
    markdown_path = converter.convert_to_markdown(pdf_path)
    print(f"✅ Markdown文件: {markdown_path}")
    
    # 第2步：初始化分析器
    llm = OpenAIProvider(model="gpt-4")
    analyzer = PaperAnalyzer(llm)
    
    # 第3步：分析论文
    print("\n开始分析论文...")
    results = analyzer.analyze_paper(markdown_path)
    
    # 第4步：保存报告
    print("\n保存分析报告...")
    report_path = analyzer.save_analysis_report(f"{Path(pdf_path).stem}_analysis.md")
    print(f"✅ 分析报告: {report_path}")
    
    # 可以访问原始结果
    print(f"\n分析了 {len(results['categories'])} 个类别")
    for cat in results['categories']:
        print(f"  - {cat['category']}: {len(cat['qa_pairs'])} 个问题")


def example_batch_processing():
    """批量处理多篇论文的示例"""
    print("=" * 60)
    print("示例4: 批量处理")
    print("=" * 60)
    
    # 准备论文列表
    papers = [
        "paper1.pdf",
        "paper2.pdf",
        "paper3.pdf",
    ]
    
    # 创建Agent
    agent = PaperReadingAgent(
        llm_provider="openai",
        model="gpt-3.5-turbo"  # 使用较便宜的模型
    )
    
    # 批量处理
    output_dir = "./batch_output"
    Path(output_dir).mkdir(exist_ok=True)
    
    for i, pdf_path in enumerate(papers, 1):
        if not Path(pdf_path).exists():
            print(f"\n[{i}/{len(papers)}] ⚠️ 跳过不存在的文件: {pdf_path}")
            continue
        
        print(f"\n[{i}/{len(papers)}] 处理: {pdf_path}")
        try:
            report_path = agent.process_paper(pdf_path, output_dir)
            print(f"✅ 完成: {report_path}")
        except Exception as e:
            print(f"❌ 失败: {e}")


def print_analysis_questions():
    """打印所有分析问题"""
    from main import PaperAnalyzer
    
    print("=" * 60)
    print("论文分析问题列表")
    print("=" * 60)
    
    for cat_info in PaperAnalyzer.ANALYSIS_QUESTIONS:
        category = cat_info["category"]
        questions = cat_info["questions"]
        
        print(f"\n## {category}\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # 打印使用说明
    print("\n论文阅读Agent - 示例脚本")
    print("\n可用的示例：")
    print("  1. 基本使用 (OpenAI)")
    print("  2. 使用Gemini")
    print("  3. 分步执行")
    print("  4. 批量处理")
    print("  5. 查看分析问题列表")
    print("  0. 退出")
    
    while True:
        choice = input("\n请选择示例 (0-5): ").strip()
        
        if choice == "0":
            print("退出")
            break
        elif choice == "1":
            example_basic_usage()
        elif choice == "2":
            example_gemini_usage()
        elif choice == "3":
            example_custom_analysis()
        elif choice == "4":
            example_batch_processing()
        elif choice == "5":
            print_analysis_questions()
        else:
            print("❌ 无效选择，请输入0-5")
