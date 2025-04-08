import pandas as pd
import json
import os
from pathlib import Path

def excel_to_json(excel_file, output_json_file):
    # 读取Excel文件
    df = pd.read_excel(excel_file)
    
    # 将所有的NaN值替换为空字符串
    df = df.fillna("")
    
    # 创建结果列表
    results = []
    
    # 获取Excel文件名作为source_file
    source_file = os.path.basename(excel_file)
    
    # 遍历每一行数据
    for _, row in df.iterrows():
        # 创建每行的数据字典
        entry = {
            "source_file": source_file,
            "Reference_id": str(row.get("Reference_ID", "")),
            "topic_name": str(row.get("topic_name", "")),
            "es_title": str(row.get("Title", "")),
            "Background/Purpose": str(row.get("Background/Purpose", "")),
            "Methods": str(row.get("Methods", "")),
            "Results/Findings": str(row.get("Results/Findings", "")),
            "Conclusion/Interpretation": str(row.get("Conclusion/Interpretation", "")),
            "Keywords": str(row.get("Keywords", "")),
            "MeSH_Terms": str(row.get("MeSH_Terms", ""))
        }
        # 确保所有值都是字符串，并且NaN被转换为空字符串
        entry = {k: v if v != "nan" else "" for k, v in entry.items()}
        results.append(entry)
    
    # 将数据写入JSON文件
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"文件处理完成: {source_file} -> {os.path.basename(output_json_file)}")

def process_excel_folder(input_folder, output_folder):
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取所有Excel文件
    excel_files = []
    for ext in ['.xlsx', '.xls']:
        excel_files.extend(list(Path(input_folder).glob(f'*{ext}')))
    
    if not excel_files:
        print(f"在文件夹 {input_folder} 中没有找到Excel文件")
        return
    
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    # 处理每个Excel文件
    for excel_file in excel_files:
        # 生成对应的JSON文件名
        json_filename = excel_file.stem + '.json'
        output_json_path = os.path.join(output_folder, json_filename)
        
        try:
            excel_to_json(str(excel_file), output_json_path)
        except Exception as e:
            print(f"处理文件 {excel_file.name} 时出错: {str(e)}")

if __name__ == "__main__":
    # 设置输入输出文件夹路径
    input_folder = "reference_extra/pubmedinfo_Eng"  # 替换为您的Excel文件所在文件夹路径
    output_folder = "reference_extra/Eng_json_extra"  # 替换为您想要保存JSON文件的文件夹路径
    
    # 执行批量转换
    process_excel_folder(input_folder, output_folder)
