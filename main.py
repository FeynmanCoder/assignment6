"""
论文阅读Agent - 用于分析论文并学习论文写作
支持多种LLM提供商（OpenAI、Gemini等）
"""

import os
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
import json
from pathlib import Path


class LLMProvider(ABC):
    """LLM提供商的抽象基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送消息并获取回复"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI (ChatGPT) 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("需要提供OpenAI API密钥")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送消息到OpenAI并获取回复"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    """Google Gemini 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("需要提供Gemini API密钥")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("请安装google-generativeai库: pip install google-generativeai")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送消息到Gemini并获取回复"""
        # 将OpenAI格式的消息转换为Gemini格式
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        response = self.client.generate_content(prompt)
        return response.text


class PDFConverter:
    """将PDF转换为Markdown的转换器"""
    
    def __init__(self):
        pass
    
    def convert_to_markdown(self, pdf_path: str, output_dir: Optional[str] = None) -> str:
        """
        将PDF转换为Markdown
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果不指定则使用PDF同目录
            
        Returns:
            转换后的markdown文件路径
        """
        try:
            import pymupdf4llm
        except ImportError:
            raise ImportError("请安装pymupdf4llm库: pip install pymupdf4llm")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        # 转换PDF到markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # 确定输出路径
        if output_dir:
            output_path = Path(output_dir) / f"{pdf_path.stem}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = pdf_path.with_suffix('.md')
        
        # 保存markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        
        print(f"PDF已转换为Markdown: {output_path}")
        return str(output_path)


class PaperAnalyzer:
    """论文分析器 - 核心类"""
    
    # 论文分析问题模板
    ANALYSIS_QUESTIONS = [
        {
            "category": "基本信息",
            "questions": [
                "这篇论文发表在什么平台（期刊或会议）？该平台在该领域的权威性如何？",
                "这篇论文属于什么研究领域？主要研究方向是什么？",
                "这篇论文的主要创新点是什么？与现有工作相比有哪些突破？",
            ]
        },
        {
            "category": "论文结构与写作",
            "questions": [
                "这篇论文展现了研究工作的哪些方面（如问题定义、方法设计、实验验证、结果分析等）？",
                "作者是如何安排这些方面的先后顺序的？它们之间的逻辑关联是如何排布的？",
                "论文每个章节的主要内容是什么？章节之间如何过渡和衔接？",
                "论文的摘要和结论分别强调了哪些内容？它们如何呼应？",
            ]
        },
        {
            "category": "图表分析",
            "questions": [
                "论文包含哪些图片和表格？每个图表分别介绍了论文工作的哪些方面？",
                "这些图表在论文中的位置如何安排？它们如何与文字内容相关联？",
                "哪些图表最能体现论文的核心贡献和创新点？",
                "图表的设计（如配色、布局、标注）有什么特点？它们如何帮助读者理解内容？",
            ]
        },
        {
            "category": "写作建议",
            "questions": [
                "如果我要发表类似的工作，应该如何组织论文结构？",
                "我应该在论文中重点呈现哪些工作内容？哪些内容需要详细描述，哪些可以简略？",
                "我应该把哪些工作通过图片或表格呈现出来？如何设计这些图表？",
                "论文的语言表达有什么特点？如何保持学术性的同时提高可读性？",
                "这篇论文在写作上有哪些值得学习的地方？又有哪些可以改进的地方？",
            ]
        },
        {
            "category": "深度思考",
            "questions": [
                "这篇论文解决了什么核心问题？为什么这个问题重要？",
                "论文的方法论有什么独特之处？为什么作者选择这种方法？",
                "实验设计如何验证论文的核心假设？实验的完整性和说服力如何？",
                "论文的局限性是什么？未来可能的研究方向有哪些？",
                "这篇论文对我自己的研究有什么启发？",
            ]
        }
    ]
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.analysis_results = {}
    
    def analyze_paper(self, markdown_path: str) -> Dict[str, any]:
        """
        分析论文并回答所有问题
        
        Args:
            markdown_path: 论文markdown文件路径
            
        Returns:
            分析结果字典
        """
        # 读取论文内容
        with open(markdown_path, 'r', encoding='utf-8') as f:
            paper_content = f.read()
        
        print("开始分析论文...")
        results = {
            "paper_path": markdown_path,
            "categories": []
        }
        
        # 对每个类别的问题进行分析
        for category_info in self.ANALYSIS_QUESTIONS:
            category = category_info["category"]
            questions = category_info["questions"]
            
            print(f"\n分析类别: {category}")
            category_result = {
                "category": category,
                "qa_pairs": []
            }
            
            for i, question in enumerate(questions, 1):
                print(f"  问题 {i}/{len(questions)}: {question[:50]}...")
                
                # 构建提示词
                messages = [
                    {
                        "role": "system",
                        "content": "你是一位资深的学术论文写作专家，擅长分析论文结构和写作技巧。"
                    },
                    {
                        "role": "user",
                        "content": f"""请仔细阅读以下论文内容，并回答问题。

论文内容：
{paper_content}

问题：{question}

请提供详细、专业的回答，并给出具体的例子和分析。"""
                    }
                ]
                
                # 获取LLM回答
                answer = self.llm.chat(messages)
                
                category_result["qa_pairs"].append({
                    "question": question,
                    "answer": answer
                })
            
            results["categories"].append(category_result)
        
        self.analysis_results = results
        return results
    
    def save_analysis_report(self, output_path: str) -> str:
        """
        将分析结果保存为Markdown报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        if not self.analysis_results:
            raise ValueError("没有可保存的分析结果，请先运行analyze_paper()")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 论文分析报告\n\n")
            f.write(f"**分析论文**: {self.analysis_results['paper_path']}\n\n")
            f.write(f"**生成时间**: {self._get_current_time()}\n\n")
            f.write("---\n\n")
            
            for category_result in self.analysis_results["categories"]:
                category = category_result["category"]
                f.write(f"## {category}\n\n")
                
                for qa_pair in category_result["qa_pairs"]:
                    question = qa_pair["question"]
                    answer = qa_pair["answer"]
                    
                    f.write(f"### {question}\n\n")
                    f.write(f"{answer}\n\n")
                    f.write("---\n\n")
        
        print(f"\n分析报告已保存: {output_path}")
        return str(output_path)
    
    @staticmethod
    def _get_current_time() -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PaperReadingAgent:
    """论文阅读Agent - 主入口类"""
    
    def __init__(self, llm_provider: str = "openai", **llm_kwargs):
        """
        初始化论文阅读Agent
        
        Args:
            llm_provider: LLM提供商 ("openai" 或 "gemini")
            **llm_kwargs: LLM提供商的额外参数
        """
        # 初始化LLM
        if llm_provider.lower() == "openai":
            self.llm = OpenAIProvider(**llm_kwargs)
        elif llm_provider.lower() == "gemini":
            self.llm = GeminiProvider(**llm_kwargs)
        else:
            raise ValueError(f"不支持的LLM提供商: {llm_provider}")
        
        # 初始化PDF转换器和论文分析器
        self.pdf_converter = PDFConverter()
        self.analyzer = PaperAnalyzer(self.llm)
    
    def process_paper(self, pdf_path: str, output_dir: Optional[str] = None) -> str:
        """
        处理论文的完整流程
        
        Args:
            pdf_path: PDF论文路径
            output_dir: 输出目录
            
        Returns:
            分析报告的路径
        """
        print("=" * 60)
        print("论文阅读Agent - 开始处理")
        print("=" * 60)
        
        # 步骤1: 转换PDF到Markdown
        print("\n步骤1: 转换PDF到Markdown...")
        markdown_path = self.pdf_converter.convert_to_markdown(pdf_path, output_dir)
        
        # 步骤2: 分析论文
        print("\n步骤2: 分析论文...")
        self.analyzer.analyze_paper(markdown_path)
        
        # 步骤3: 生成报告
        print("\n步骤3: 生成分析报告...")
        pdf_name = Path(pdf_path).stem
        if output_dir:
            report_path = Path(output_dir) / f"{pdf_name}_analysis.md"
        else:
            report_path = Path(pdf_path).parent / f"{pdf_name}_analysis.md"
        
        report_path = self.analyzer.save_analysis_report(str(report_path))
        
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"Markdown文件: {markdown_path}")
        print(f"分析报告: {report_path}")
        
        return report_path
    
    def batch_process_papers(self, papers_dir: str = "papers", output_dir: str = "output") -> List[str]:
        """
        批量处理papers文件夹中的所有PDF论文
        
        Args:
            papers_dir: 存放PDF论文的文件夹路径（默认: papers）
            output_dir: 输出目录（默认: output）
            
        Returns:
            所有生成的分析报告路径列表
        """
        papers_path = Path(papers_dir)
        output_path = Path(output_dir)
        
        # 确保目录存在
        if not papers_path.exists():
            papers_path.mkdir(parents=True, exist_ok=True)
            print(f"已创建论文文件夹: {papers_path}")
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"已创建输出文件夹: {output_path}")
        
        # 查找所有PDF文件
        pdf_files = list(papers_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"\n⚠️  在 {papers_path} 文件夹中没有找到PDF文件")
            print(f"请将PDF论文放入 {papers_path} 文件夹后再运行程序")
            return []
        
        print(f"\n找到 {len(pdf_files)} 篇论文待处理")
        print("=" * 60)
        
        results = []
        successful = 0
        failed = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n{'=' * 60}")
            print(f"处理进度: [{i}/{len(pdf_files)}]")
            print(f"当前论文: {pdf_file.name}")
            print("=" * 60)
            
            try:
                report_path = self.process_paper(str(pdf_file), str(output_path))
                results.append(report_path)
                successful += 1
                print(f"\n✅ 成功: {pdf_file.name}")
            except Exception as e:
                failed += 1
                print(f"\n❌ 失败: {pdf_file.name}")
                print(f"错误信息: {e}")
                import traceback
                traceback.print_exc()
        
        # 打印总结
        print("\n" + "=" * 60)
        print("批量处理完成！")
        print("=" * 60)
        print(f"总计: {len(pdf_files)} 篇论文")
        print(f"成功: {successful} 篇")
        print(f"失败: {failed} 篇")
        print(f"\n所有结果已保存到: {output_path.absolute()}")
        
        return results


def main():
    """主函数 - 支持单个文件和批量处理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="论文阅读Agent - 自动批量分析papers文件夹中的所有论文",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 批量处理papers文件夹中的所有论文（推荐）
  python main.py
  
  # 批量处理，使用Gemini
  python main.py --provider gemini
  
  # 处理单个PDF文件
  python main.py --single paper.pdf
  
  # 指定自定义文件夹
  python main.py --papers-dir ./my_papers --output-dir ./my_output
        """
    )
    
    # 模式选择
    parser.add_argument("--single", metavar="PDF_FILE", 
                        help="单文件模式：处理指定的PDF文件")
    
    # 批量处理参数
    parser.add_argument("--papers-dir", default="papers",
                        help="论文文件夹路径 (默认: papers)")
    parser.add_argument("--output-dir", default="output",
                        help="输出目录路径 (默认: output)")
    
    # LLM配置
    parser.add_argument("--provider", choices=["openai", "gemini"], default="openai",
                        help="LLM提供商 (默认: openai)")
    parser.add_argument("--model", help="模型名称 (如: gpt-4, gemini-pro)")
    parser.add_argument("--api-key", help="API密钥 (也可通过环境变量设置)")
    
    args = parser.parse_args()
    
    # 准备LLM参数
    llm_kwargs = {}
    if args.api_key:
        llm_kwargs["api_key"] = args.api_key
    if args.model:
        llm_kwargs["model"] = args.model
    
    # 创建Agent
    try:
        print("\n初始化论文阅读Agent...")
        print(f"LLM提供商: {args.provider}")
        if args.model:
            print(f"模型: {args.model}")
        
        agent = PaperReadingAgent(llm_provider=args.provider, **llm_kwargs)
        
        # 判断是单文件模式还是批量处理模式
        if args.single:
            # 单文件模式
            print(f"\n📄 单文件模式")
            agent.process_paper(args.single, args.output_dir)
        else:
            # 批量处理模式（默认）
            print(f"\n📚 批量处理模式")
            print(f"论文文件夹: {Path(args.papers_dir).absolute()}")
            print(f"输出文件夹: {Path(args.output_dir).absolute()}")
            agent.batch_process_papers(args.papers_dir, args.output_dir)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
