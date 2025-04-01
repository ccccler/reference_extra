import pandas as pd

def extract_lines(md_text):
    # 用于存储提取的行
    lines = []
    
    # 按行分割文本
    text_lines = md_text.split('\n')
    
    # 遍历每一行
    for i, line in enumerate(text_lines, 1):
        # 跳过空行
        if line.strip():
            lines.append({
                'Number': i,
                'Content': line.strip()
            })
    
    # 创建DataFrame
    df = pd.DataFrame(lines)
    
    # 保存为Excel文件
    output_file = 'content_lines.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"成功提取了 {len(lines)} 行内容并保存到 {output_file}")

# 读取MD文件内容
with open('Chinese_pre/CSCO_2024.md', 'r', encoding='utf-8') as file:
    md_content = file.read()

# 处理文件
extract_lines(md_content)
