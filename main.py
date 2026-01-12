"""
论文阅读Agent - 用于分析论文并学习论文写作
支持多种LLM提供商（OpenAI、Gemini等）
"""

import os
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
import json
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载.env文件
except ImportError:
    pass  # 如果没有安装python-dotenv，跳过


class LLMProvider(ABC):
    """LLM提供商的抽象基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送消息并获取回复"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI (ChatGPT) 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model
        
        if not self.api_key:
            raise ValueError("需要提供OpenAI API密钥")
        
        try:
            from openai import OpenAI
            # 创建客户端，支持自定义base_url
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self.client = OpenAI(**client_kwargs)
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
    
    def __init__(self, use_mineru: bool = False, mineru_token: Optional[str] = None):
        """
        初始化PDF转换器
        
        Args:
            use_mineru: 是否使用MinerU API（更好地支持图片和公式）
            mineru_token: MinerU API token（可从环境变量MINERU_TOKEN读取）
        """
        self.use_mineru = use_mineru
        self.mineru_token = mineru_token or os.getenv('MINERU_TOKEN')
        
        if use_mineru and not self.mineru_token:
            print("警告: 未提供MinerU token，将回退到pymupdf4llm")
            self.use_mineru = False
    
    def convert_to_markdown(self, pdf_path: str, output_dir: Optional[str] = None) -> str:
        """
        将PDF转换为Markdown（支持图片和公式提取）
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果不指定则使用PDF同目录
            
        Returns:
            转换后的markdown文件路径
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        # 确定输出路径
        if output_dir:
            output_path = Path(output_dir) / f"{pdf_path.stem}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = pdf_path.with_suffix('.md')
        
        # 如果已存在转换结果，跳过转换
        if output_path.exists():
            print(f"⚠️  已存在Markdown文件，跳过转换: {output_path}")
            print(f"提示：如需重新转换，请删除output文件夹或该文件")
            return str(output_path)
        
        # 尝试使用MinerU API（更好的图片和公式支持）
        if self.use_mineru:
            print(f"📡 使用MinerU API转换PDF（支持图片和公式）...")
            try:
                return self._convert_with_mineru(pdf_path, output_path)
            except Exception as e:
                print(f"❌ MinerU转换失败，回退到pymupdf4llm: {e}")
        else:
            print(f"⚡ 使用pymupdf4llm快速转换...")
        
        # 使用pymupdf4llm作为备选
        return self._convert_with_pymupdf(pdf_path, output_path)
    
    def _convert_with_mineru(self, pdf_path: Path, output_path: Path) -> str:
        """使用MinerU API转换（支持图片和公式）"""
        import requests
        import uuid
        import time
        import zipfile
        import shutil
        
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.mineru_token}"
        }
        
        # 1. 申请上传URL
        url = "https://mineru.net/api/v4/file-urls/batch"
        data = {
            "enable_formula": True,  # 启用公式识别
            "enable_table": True,
            "model_version": "vlm",
            "files": [{"name": pdf_path.name, "data_id": str(uuid.uuid4())}]
        }
        
        response = requests.post(url, headers=header, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"申请上传失败: {result}")
        
        batch_id = result["data"]["batch_id"]
        upload_url = result["data"]["file_urls"][0]
        
        # 2. 上传PDF
        print(f"📤 正在上传PDF文件...")
        with open(pdf_path, 'rb') as f:
            upload_response = requests.put(upload_url, data=f)
            upload_response.raise_for_status()
        
        print(f"✅ 上传成功！批次ID: {batch_id}")
        print(f"⏳ 等待MinerU处理（可能需要1-3分钟）...")
        
        # 3. 轮询结果
        retrieve_url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        max_retry = 180
        retry = 0
        
        while retry < max_retry:
            time.sleep(3)
            res = requests.get(retrieve_url, headers=header)
            res.raise_for_status()
            payload = res.json()
            results = payload.get("data", {}).get("extract_result", [])
            
            if results and results[0].get("state") == "done":
                zip_url = results[0].get("full_zip_url")
                if not zip_url:
                    raise Exception("未获取到下载链接")
                
                print(f"✅ MinerU处理完成，正在下载结果...")
                
                # 4. 下载并解压结果
                zip_path = output_path.with_suffix('.zip')
                response = requests.get(zip_url, stream=True)
                response.raise_for_status()
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 5. 解压并提取markdown
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    # 提取full.md
                    if 'full.md' in zf.namelist():
                        with zf.open('full.md') as src:
                            with open(output_path, 'wb') as dst:
                                shutil.copyfileobj(src, dst)
                    
                    # 提取images文件夹
                    images_dir = output_path.parent / "images"
                    images_dir.mkdir(exist_ok=True)
                    for member in zf.namelist():
                        if member.startswith('images/'):
                            zf.extract(member, output_path.parent)
                
                print(f"PDF已转换为Markdown（含图片和公式）: {output_path}")
                return str(output_path)
            
            retry += 1
            if retry % 10 == 0:
                print(f"等待转换完成... ({retry}/{max_retry})")
        
        raise Exception("转换超时")
    
    def _convert_with_pymupdf(self, pdf_path: Path, output_path: Path) -> str:
        """使用pymupdf4llm转换（备选方案）"""
        try:
            import pymupdf4llm
        except ImportError:
            raise ImportError("请安装pymupdf4llm库: pip install pymupdf4llm")
        
        # 转换PDF到markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # 保存markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        
        print(f"PDF已转换为Markdown: {output_path}")
        return str(output_path)


class PaperAnalyzer:
    """论文分析器 - 核心类"""
    
    @staticmethod
    def extract_images_from_markdown(markdown_path: Path) -> List[Path]:
        """从markdown文件中提取图片路径"""
        import re
        
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 ![...](images/xxx.png) 格式
        image_pattern = r'!\[.*?\]\((images/[^)]+)\)'
        image_refs = re.findall(image_pattern, content)
        
        # 转换为绝对路径
        base_dir = markdown_path.parent
        image_paths = []
        for ref in image_refs:
            img_path = base_dir / ref
            if img_path.exists():
                image_paths.append(img_path)
        
        return image_paths
    
    @staticmethod
    def image_to_base64(image_path: Path) -> str:
        """将图片转换为base64编码"""
        import base64
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 获取图片格式
        ext = image_path.suffix.lower().lstrip('.')
        if ext == 'jpg':
            ext = 'jpeg'
        
        base64_str = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/{ext};base64,{base64_str}"
    
    # 论文分析问题模板
    ANALYSIS_QUESTIONS = [
        {
            "category": "基本信息",
            "questions": [
                "这篇论文发表在什么平台（期刊或会议）？该平台在该领域的权威性如何？",
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
        md_path = Path(markdown_path)
        with open(md_path, 'r', encoding='utf-8') as f:
            paper_content = f.read()
        
        # 提取图片
        image_paths = self.extract_images_from_markdown(md_path)
        print(f"开始分析论文...")
        print(f"论文字数: {len(paper_content)}")
        print(f"论文图片数: {len(image_paths)}")
        
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
                
                # 根据类别选择不同的提示词策略
                if category == "基本信息":
                    # 基本信息类：严格精简
                    requirement = "要求：2-3个要点，每点不超过20字，总共<60字。"
                    system_prompt = """你是论文分析专家。回答必须极简：

严格要求：
1. 只用要点列表，不用段落
2. 2-3个要点，每个不超过20字
3. 直接给结论，不要解释过程
4. 用数据/名词而非描述
5. 总字数<60字
6. 如果看到图片，优先分析图片内容"""
                else:
                    # 其他类别：宽松限制，但要求简洁
                    requirement = "要求：10个要点以内，每个要点不超过100字。请你尽可能简洁地回答，切中要点，不要有冗余的表达。"
                    system_prompt = """你是论文分析专家。回答要简洁明了：

要求：
1. 使用要点列表形式，逻辑清晰
2. 最多10个要点，每个要点不超过100字
3. 切中要点，避免冗余表达
4. 结合论文的具体内容和图片进行分析
5. 用具体的数据、方法名、章节名等实质性信息
6. 如果看到图片，优先分析图片传达的核心信息"""
                
                # 构建用户消息内容（支持多模态）
                user_content = [
                    {
                        "type": "text",
                        "text": f"""{paper_content}

问题：{question}

{requirement}"""
                    }
                ]
                
                # 添加图片（限制前5张，避免token过多）
                for img_path in image_paths[:5]:
                    try:
                        base64_image = self.image_to_base64(img_path)
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": base64_image}
                        })
                    except Exception as e:
                        print(f"    警告: 无法加载图片 {img_path.name}: {e}")
                
                # 构建消息
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_content
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
    
    def __init__(self, llm_provider: str = "openai", use_mineru: bool = True, **llm_kwargs):
        """
        初始化论文阅读Agent
        
        Args:
            llm_provider: LLM提供商 ("openai" 或 "gemini")
            use_mineru: 是否使用MinerU API转换PDF（更好的图片和公式支持）
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
        self.pdf_converter = PDFConverter(use_mineru=use_mineru)
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
        
        # 提示用户检查markdown文件
        print("\n" + "=" * 60)
        print(f"✅ Markdown转换完成：{markdown_path}")
        print("\n您可以先检查转换结果：")
        print(f"  - Markdown文件: {markdown_path}")
        if Path(markdown_path).parent.joinpath('images').exists():
            print(f"  - 图片文件夹: {Path(markdown_path).parent / 'images'}")
        print("\n按回车键继续分析，或 Ctrl+C 中止...")
        print("=" * 60)
        try:
            input()
        except KeyboardInterrupt:
            print("\n\n已取消分析")
            return markdown_path
        
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
    parser.add_argument("--model", help="模型名称 (如: gpt-5, gemini-pro)")
    parser.add_argument("--api-key", help="API密钥 (也可通过环境变量设置)")
    
    # PDF转换配置
    parser.add_argument("--no-mineru", action="store_true",
                        help="不使用MinerU API，改用pymupdf4llm快速模式（图片公式支持有限）")
    
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
        
        # 默认使用MinerU，除非指定--no-mineru
        use_mineru = not args.no_mineru
        if use_mineru:
            print(f"PDF转换: MinerU API（完美支持图片和公式）")
        else:
            print(f"PDF转换: pymupdf4llm（快速模式，图片公式支持有限）")
        
        agent = PaperReadingAgent(llm_provider=args.provider, use_mineru=use_mineru, **llm_kwargs)
        
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
