import json
import os
from difflib import SequenceMatcher
import re
import pandas as pd

def clean_string(s):
    """清理字符串，移除特殊字符并转换为小写"""
    # 移除特殊字符，只保留字母、数字和空格
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    # 转换为小写
    return s.lower().strip()

def similarity_ratio(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, clean_string(a), clean_string(b)).ratio()

def match_pdfs_with_titles(json_file, pdf_folder, output_file, excel_output, similarity_threshold=0.6):
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取PDF文件夹中所有PDF文件名
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    # 记录匹配结果
    results = []
    
    # 遍历JSON数据
    for item in data:
        title = item.get('Title', '')
        best_match = None
        best_ratio = 0
        
        # 对每个标题尝试匹配所有PDF文件名
        for pdf_file in pdf_files:
            # 计算相似度
            ratio = similarity_ratio(title, pdf_file)
            
            # 更新最佳匹配
            if ratio > best_ratio and ratio >= similarity_threshold:
                best_ratio = ratio
                best_match = pdf_file
        
        # 如果找到匹配，更新pdf_path
        if best_match:
            item['pdf_path'] = os.path.join(pdf_folder, best_match)
        
        # 记录结果
        results.append({
            'Title': title,
            'Matched PDF': best_match if best_match else 'No Match',
            'Similarity Ratio': best_ratio
        })
    
    # 保存更新后的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    # 将结果保存到Excel文件
    df = pd.DataFrame(results)
    df.to_excel(excel_output, index=False)
    
    # 打印统计信息
    matched_count = sum(1 for result in results if result['Matched PDF'] != 'No Match')
    print(f"总条目数: {len(data)}")
    print(f"成功匹配数: {matched_count}")
    print(f"未匹配数: {len(data) - matched_count}")

# 使用示例
json_file = "./HCM/4.7+4.8/without_pdf.json"  # 你的无PDF路径的JSON文件
pdf_folder = "./HCM/4.7+4.8/comp_pdf"  # 你的PDF文件夹路径
output_file = "./HCM/4.7+4.8/updated_with_pdf_paths.json"  # 输出JSON文件名
excel_output = "./HCM/4.7+4.8/matching_results.xlsx"  # 输出Excel文件名

match_pdfs_with_titles(json_file, pdf_folder, output_file, excel_output)
