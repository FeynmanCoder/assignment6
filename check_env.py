"""
环境检查脚本 - 验证所有依赖是否正确安装
"""

import sys


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"  当前版本: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("  ✅ Python版本符合要求 (>= 3.7)")
        return True
    else:
        print("  ❌ Python版本过低，需要 >= 3.7")
        return False


def check_package(package_name, import_name=None):
    """检查单个包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"  ✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"  ❌ {package_name} 未安装")
        return False


def check_required_packages():
    """检查必需的包"""
    print("\n检查必需的包...")
    
    packages = [
        ("openai", "openai"),
        ("google-generativeai", "google.generativeai"),
        ("pymupdf4llm", "pymupdf4llm"),
    ]
    
    all_installed = True
    for pkg_name, import_name in packages:
        if not check_package(pkg_name, import_name):
            all_installed = False
    
    return all_installed


def check_optional_packages():
    """检查可选的包"""
    print("\n检查可选的包...")
    
    packages = [
        ("python-dotenv", "dotenv"),
    ]
    
    for pkg_name, import_name in packages:
        check_package(pkg_name, import_name)


def check_api_keys():
    """检查API密钥配置"""
    print("\n检查API密钥配置...")
    import os
    
    # 尝试加载 .env 文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("  ✅ 成功加载 .env 文件")
    except:
        print("  ⚠️  未安装python-dotenv或无.env文件")
    
    # 检查OpenAI密钥
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"  ✅ OpenAI API密钥已配置 (长度: {len(openai_key)})")
    else:
        print("  ⚠️  未配置OpenAI API密钥")
    
    # 检查Gemini密钥
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"  ✅ Gemini API密钥已配置 (长度: {len(gemini_key)})")
    else:
        print("  ⚠️  未配置Gemini API密钥")
    
    if not openai_key and not gemini_key:
        print("  ⚠️  警告: 至少需要配置一个LLM提供商的API密钥")
        return False
    
    return True


def check_main_file():
    """检查主程序文件"""
    print("\n检查主程序文件...")
    from pathlib import Path
    
    files = ["main.py", "README.md", "requirements.txt"]
    all_exist = True
    
    for filename in files:
        if Path(filename).exists():
            print(f"  ✅ {filename} 存在")
        else:
            print(f"  ❌ {filename} 不存在")
            all_exist = False
    
    return all_exist


def test_pdf_conversion():
    """测试PDF转换功能"""
    print("\n测试PDF转换功能...")
    
    try:
        from main import PDFConverter
        converter = PDFConverter()
        print("  ✅ PDFConverter初始化成功")
        return True
    except Exception as e:
        print(f"  ❌ PDFConverter初始化失败: {e}")
        return False


def test_llm_providers():
    """测试LLM提供商"""
    print("\n测试LLM提供商...")
    import os
    
    # 测试OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            from main import OpenAIProvider
            # 不实际调用API，只测试初始化
            provider = OpenAIProvider()
            print("  ✅ OpenAIProvider初始化成功")
        except Exception as e:
            print(f"  ❌ OpenAIProvider初始化失败: {e}")
    else:
        print("  ⚠️  跳过OpenAI测试（未配置密钥）")
    
    # 测试Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            from main import GeminiProvider
            provider = GeminiProvider()
            print("  ✅ GeminiProvider初始化成功")
        except Exception as e:
            print(f"  ❌ GeminiProvider初始化失败: {e}")
    else:
        print("  ⚠️  跳过Gemini测试（未配置密钥）")


def print_summary(checks):
    """打印总结"""
    print("\n" + "=" * 60)
    print("环境检查总结")
    print("=" * 60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 环境配置完美！可以开始使用了。")
        print("\n下一步：")
        print("  1. 准备一篇PDF论文")
        print("  2. 运行: python main.py your_paper.pdf")
        print("  3. 查看生成的分析报告")
    else:
        print("\n⚠️  部分检查未通过，请根据上述提示修复问题。")
        print("\n常见解决方案：")
        print("  - 安装缺失的包: pip install -r requirements.txt")
        print("  - 配置API密钥: 复制 .env.example 为 .env 并填入密钥")
        print("  - 确保Python版本 >= 3.7")


def main():
    """主函数"""
    print("=" * 60)
    print("论文阅读Agent - 环境检查")
    print("=" * 60)
    
    checks = {
        "Python版本": check_python_version(),
        "必需的包": check_required_packages(),
        "主程序文件": check_main_file(),
        "API密钥配置": check_api_keys(),
        "PDF转换功能": test_pdf_conversion(),
    }
    
    # 可选检查
    check_optional_packages()
    test_llm_providers()
    
    # 打印总结
    print_summary(checks)
    
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    exit(main())
