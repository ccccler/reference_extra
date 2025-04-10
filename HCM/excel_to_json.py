import pandas as pd
import json

def excel_to_json(excel_file, output_json_file):
    # 读取 Excel 文件，将 Publication Year 列作为字符串读取
    df = pd.read_excel(
        excel_file,
        dtype={'Publication Year': str}  # 指定 Publication Year 列为字符串类型
    )
    
    # 确保 Publication Year 列的值都是字符串
    if 'Publication Year' in df.columns:
        df['Publication Year'] = df['Publication Year'].astype(str)
    
    # 将 DataFrame 转换为字典列表
    records = df.to_dict('records')
    
    # 为每条记录添加 pdf 路径
    for record in records:
        # 确保 Title 字段存在
        if 'Title' in record:
            record['pdf_path'] = f"./artical/4.8files/{record['Title']}.pdf"
        else:
            record['pdf_path'] = ""  # 如果没有 Title 字段，设置为空字符串
    
    # 将数据保存为 JSON 文件
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {output_json_file}")

# 使用示例
if __name__ == "__main__":
    excel_file = "./HCM/HCM4.8.xlsx"  # 替换为你的 Excel 文件路径
    output_json_file = "./HCM/HCM4.8.json"     # 输出的 JSON 文件路径
    excel_to_json(excel_file, output_json_file)
