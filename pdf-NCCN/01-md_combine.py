import os
import re
import pandas as pd
from pathlib import Path

def extract_text_blocks(md_file_path):
    """
    从markdown文件中提取文本块，按照编号条目拆分
    返回: 包含(文件名, 块索引, 内容)的列表
    """
    blocks = []
    file_name = os.path.basename(md_file_path)
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        # 逐行读取文件
        lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            # 跳过空行
            if not line:
                continue
                
            # 使用正则表达式匹配行首数字
            match = re.match(r'^\s*(\d+)\s+(.+)$', line)
            if match:
                index = int(match.group(1))  # 获取原始编号
                content = match.group(2)      # 获取内容
                blocks.append({
                    '来源文件': file_name,
                    '文本块索引': index,
                    '内容': content
                })
    
    return blocks

def process_markdown_folder(folder_path, output_excel):
    """
    处理文件夹中的所有markdown文件并输出到Excel
    """
    all_blocks = []
    folder_path = Path(folder_path)
    
    # 遍历文件夹中的所有md文件
    for md_file in folder_path.glob('*.md'):
        blocks = extract_text_blocks(md_file)
        all_blocks.extend(blocks)
    
    # 创建DataFrame并保存到Excel
    df = pd.DataFrame(all_blocks)
    # 按照来源文件和文本块索引排序
    df = df.sort_values(['来源文件', '文本块索引'])
    df.to_excel(output_excel, index=False)
    print(f'已将所有文本块保存到: {output_excel}')

# 使用示例
if __name__ == '__main__':
    input_folder = './Chinese_pre'  # 替换为您的markdown文件夹路径
    output_file = 'output.xlsx'  # 输出的Excel文件名
    
    process_markdown_folder(input_folder, output_file)
