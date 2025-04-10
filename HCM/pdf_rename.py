import os
import re

def rename_pdfs(folder_path):
    # 确保文件夹路径存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在！")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            # 获取完整的文件路径
            old_path = os.path.join(folder_path, filename)
            
            # 使用正则表达式提取论文标题（在最后一个 " - " 之后的部分）
            parts = filename.split(' - ')
            if len(parts) >= 3:
                new_name = parts[-1]  # 获取最后一部分（论文标题）
                
                # 确保新文件名仍然包含.pdf扩展名
                if not new_name.lower().endswith('.pdf'):
                    new_name += '.pdf'
                
                # 构建新的完整路径
                new_path = os.path.join(folder_path, new_name)
                
                try:
                    # 重命名文件
                    os.rename(old_path, new_path)
                    print(f'已重命名: {filename} -> {new_name}')
                except Exception as e:
                    print(f'重命名 {filename} 时出错: {str(e)}')

# 使用示例
folder_path = '4.8files_pdf去重'  # 替换为你的PDF文件夹路径
rename_pdfs(folder_path)
