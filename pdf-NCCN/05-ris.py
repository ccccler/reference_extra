import pandas as pd

def create_ris_entry(row):
    """将单行参考文献信息转换为RIS格式"""
    ris_entry = []
    
    # 开始一个新记录
    ris_entry.append("TY  - JOUR")  # 假设都是期刊文章，如果有其他类型可以修改
    
    # 添加作者 (可以处理多个作者)
    authors = str(row['authors']).split(',')  # 假设作者用逗号分隔
    for author in authors:
        author = author.strip()
        if author:
            ris_entry.append(f"AU  - {author}")
    
    # 添加标题
    if pd.notna(row['title']):
        ris_entry.append(f"TI  - {row['title']}")
    
    # 添加期刊名称
    if pd.notna(row['journal']):
        # ris_entry.append(f"JO  - {row['journal']}")
        ris_entry.append(f"JF  - {row['journal']}")  # 完整期刊名称
    
    # 添加发表日期
    if pd.notna(row['year']):
        # 直接使用year字段的值，不进行日期转换
        year_str = str(row['year']).strip()
        ris_entry.append(f"PY  - {year_str}")
    
    # 结束记录
    ris_entry.append("ER  - ")
    
    return "\n".join(ris_entry)

def convert_to_ris(input_file, output_file):
    """将Excel/CSV文件转换为RIS格式"""
    try:
        # 尝试读取Excel文件
        df = pd.read_excel(input_file)
    except:
        # 如果不是Excel，尝试读取CSV
        df = pd.read_csv(input_file)
    
    # 创建RIS格式的文本
    ris_content = []
    for _, row in df.iterrows():
        ris_content.append(create_ris_entry(row))
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(ris_content))

# 使用示例
if __name__ == "__main__":
    input_file = "./inside_reference/NCCN_2024v5_middle_output.xlsx"  # 你的输入文件名
    output_file = "NCCN_2024v5_middle_references.ris"  # 输出文件名
    
    convert_to_ris(input_file, output_file)
    print("转换完成！")
