"""
清理output文件夹的脚本
用于删除已生成的文件，以便重新转换
"""

import shutil
from pathlib import Path
import argparse


def clean_output(output_dir: str = "output", keep_structure: bool = True):
    """
    清理output文件夹
    
    Args:
        output_dir: 输出目录路径
        keep_structure: 是否保留文件夹结构（只删除内容）
    """
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"✅ {output_dir} 文件夹不存在，无需清理")
        return
    
    # 统计要删除的文件
    md_files = list(output_path.rglob("*.md"))
    json_files = list(output_path.rglob("*.json"))
    zip_files = list(output_path.rglob("*.zip"))
    images_dirs = [d for d in output_path.rglob("images") if d.is_dir()]
    
    total_files = len(md_files) + len(json_files) + len(zip_files)
    
    if total_files == 0 and len(images_dirs) == 0:
        print(f"✅ {output_dir} 文件夹已经是空的")
        return
    
    print(f"\n将要删除 {output_dir} 中的文件：")
    print(f"  - Markdown文件: {len(md_files)}")
    print(f"  - JSON文件: {len(json_files)}")
    print(f"  - ZIP文件: {len(zip_files)}")
    print(f"  - images文件夹: {len(images_dirs)}")
    print(f"总计: {total_files} 个文件 + {len(images_dirs)} 个图片文件夹")
    
    # 确认
    confirm = input("\n确认删除？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消清理")
        return
    
    # 删除文件
    deleted = 0
    
    for f in md_files + json_files + zip_files:
        try:
            f.unlink()
            deleted += 1
        except Exception as e:
            print(f"删除失败 {f}: {e}")
    
    # 删除images文件夹
    for d in images_dirs:
        try:
            shutil.rmtree(d)
            print(f"✅ 已删除: {d}")
        except Exception as e:
            print(f"删除失败 {d}: {e}")
    
    # 删除空文件夹（如果不保留结构）
    if not keep_structure:
        try:
            shutil.rmtree(output_path)
            print(f"✅ 已删除整个文件夹: {output_path}")
        except Exception as e:
            print(f"删除失败: {e}")
    
    print(f"\n✅ 清理完成！删除了 {deleted} 个文件和 {len(images_dirs)} 个图片文件夹")


def main():
    parser = argparse.ArgumentParser(description="清理output文件夹")
    parser.add_argument("--output-dir", default="output", help="输出目录路径（默认: output）")
    parser.add_argument("--remove-all", action="store_true", help="删除整个output文件夹（而非只删除内容）")
    parser.add_argument("--force", action="store_true", help="强制删除，不询问确认")
    
    args = parser.parse_args()
    
    if args.force:
        # 强制删除模式
        output_path = Path(args.output_dir)
        if output_path.exists():
            if args.remove_all:
                shutil.rmtree(output_path)
                print(f"✅ 已删除: {output_path}")
            else:
                for item in output_path.rglob("*"):
                    if item.is_file():
                        item.unlink()
                print(f"✅ 已清空: {output_path}")
        else:
            print(f"✅ {args.output_dir} 不存在")
    else:
        # 交互式删除
        clean_output(args.output_dir, keep_structure=not args.remove_all)


if __name__ == "__main__":
    main()
