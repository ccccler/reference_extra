import json
import pandas as pd

def combine_abstract_fields(data):
    # 需要合并的字段及其标签
    fields_to_combine = [
        ("Background", "Background: "),
        ("Methods", "Methods: "),
        ("Results/Findings", "Results: "),
        ("Conclusion/Interpretation", "Conclusion: ")
    ]
    
    # 额外需要保留的字段
    additional_fields = ['pubmed_url', 'pubmed_id', 'Title', 'MeSH_Terms']
    
    # 将DataFrame转换为字典列表
    records = data.to_dict('records')
    processed_records = []
    
    # 处理每一条记录
    for item in records:
        # 收集所有非空的字段内容
        abstract_parts = []
        for field, label in fields_to_combine:
            if field in item and pd.notna(item[field]):  # 使用pd.notna()检查非空值
                abstract_parts.append(f"{label}{item[field]}")
        
        # 创建新的记录字典
        new_record = {
            'abstract': ' '.join(abstract_parts)
        }
        
        # 添加额外字段
        for field in additional_fields:
            if field in item and pd.notna(item[field]):
                # 特殊处理PubMed-id，转换为整数后再转为字符串，去除小数点
                if field == 'PubMed-id':
                    new_record[field] = str(int(item[field]))
                else:
                    new_record[field] = item[field]
        
        processed_records.append(new_record)
        
    return processed_records

def process_excel_file(input_file, output_file):
    # 读取Excel文件
    df = pd.read_excel(input_file)
    
    # 处理数据
    processed_data = combine_abstract_fields(df)
    
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

# 使用示例
if __name__ == "__main__":
    input_file = "./pubmedinfo/00-doc_combine.xlsx"  # 输入Excel文件路径
    output_file = "abcom_output_data.json"  # 输出文件路径
    process_excel_file(input_file, output_file)
