import json

def combine_abstract_fields(data):
    # 需要合并的字段及其标签
    fields_to_combine = [
        ("Background/Purpose", "Background: "),
        ("Methods", "Methods: "),
        ("Results/Findings", "Results: "),
        ("Conclusion/Interpretation", "Conclusion: ")
    ]
    
    # 处理每一条记录
    for item in data:
        # 收集所有非空的字段内容
        abstract_parts = []
        for field, label in fields_to_combine:
            if field in item and item[field]:  # 确保字段存在且非空
                abstract_parts.append(f"{label}{item[field]}")
        
        # 用空格连接所有部分，创建新的abstract字段
        item['abstract'] = ' '.join(abstract_parts)
        
    return data

def process_json_file(input_file, output_file):
    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理数据
    processed_data = combine_abstract_fields(data)
    
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

# 使用示例
if __name__ == "__main__":
    input_file = "./reference_extra/test_data.json"  # 输入文件路径
    output_file = "./reference_extra/output_data.json"  # 输出文件路径
    process_json_file(input_file, output_file)
