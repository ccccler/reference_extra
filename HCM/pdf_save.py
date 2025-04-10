import os
import shutil
from pathlib import Path

def extract_pdf_files(source_dir, target_dir):
    # 创建目标文件夹（如果不存在）
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 遍历源文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(source_dir):
        # 处理当前文件夹中的文件
        for file in files:
            # 检查文件是否为PDF
            if file.lower().endswith('.pdf'):
                # 构建源文件和目标文件的完整路径
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                
                # 直接复制文件（如果存在则覆盖）
                shutil.copy2(source_file, target_file)
                print(f"已复制: {source_file} -> {target_file}")

# 使用示例
if __name__ == "__main__":
    # 设置源文件夹路径（包含多个子文件夹的主文件夹）
    source_directory = "4.7_files"
    # 设置目标文件夹路径（存放提取出的PDF文件的新文件夹）
    target_directory = "4.7files_pdf去重"
    
    # 执行PDF文件提取
    extract_pdf_files(source_directory, target_directory)
    print("所有PDF文件提取完成！")
