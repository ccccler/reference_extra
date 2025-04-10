import json
import os
import re
from pathlib import Path
import pandas as pd
from datetime import datetime

def normalize_title(title):
    """标准化标题字符串
    1. 转换为小写
    2. 移除所有标点符号和特殊字符
    3. 将多个空格合并为单个空格
    4. 移除首尾空格
    """
    # 转换为小写
    title = title.lower()
    # 移除标点符号和特殊字符，保留字母、数字、空格
    title = re.sub(r'[^\w\s]', '', title)
    # 将多个空格合并为一个
    title = re.sub(r'\s+', ' ', title)
    # 移除首尾空格
    title = title.strip()
    return title

def verify_titles(json_path, pdf_folder):
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取所有PDF文件名（不含扩展名）并标准化
    pdf_files = {normalize_title(Path(f).stem): Path(f).stem 
                 for f in os.listdir(pdf_folder) 
                 if f.lower().endswith('.pdf')}
    
    # 获取所有JSON中的标题并标准化
    json_titles = {normalize_title(item.get('Title', '').strip()): item.get('Title', '').strip() 
                   for item in data}
    
    # 用于存储结果
    matched = []
    fuzzy_matched = []
    missing_in_pdf = []    # JSON中有但PDF中没有
    missing_in_json = []   # PDF中有但JSON中没有
    
    # 检查JSON中的每个标题
    for norm_json_title, original_json_title in json_titles.items():
        if norm_json_title in pdf_files:
            matched.append((original_json_title, pdf_files[norm_json_title]))
        else:
            # 检查是否为子字符串
            possible_matches = [
                (pdf_original, score_similarity(norm_json_title, norm_pdf_title))
                for norm_pdf_title, pdf_original in pdf_files.items()
                if (norm_json_title in norm_pdf_title or 
                    norm_pdf_title in norm_json_title)
            ]
            
            if possible_matches:
                # 获取相似度最高的匹配
                best_match = max(possible_matches, key=lambda x: x[1])
                if best_match[1] > 0.8:  # 相似度阈值
                    fuzzy_matched.append((original_json_title, best_match[0], best_match[1]))
                else:
                    missing_in_pdf.append(original_json_title)
            else:
                missing_in_pdf.append(original_json_title)
    
    # 检查PDF中有但JSON中没有的文件
    for norm_pdf_title, original_pdf_name in pdf_files.items():
        if norm_pdf_title not in json_titles:
            # 检查是否已经在模糊匹配中
            if not any(pdf_name == original_pdf_name for _, pdf_name, _ in fuzzy_matched):
                missing_in_json.append(original_pdf_name)
    
    # 创建DataFrame对象
    exact_matches_df = pd.DataFrame(matched, columns=['JSON标题', 'PDF文件名'])
    fuzzy_matches_df = pd.DataFrame(fuzzy_matched, columns=['JSON标题', 'PDF文件名', '相似度'])
    missing_in_pdf_df = pd.DataFrame(missing_in_pdf, columns=['JSON标题'])
    missing_in_json_df = pd.DataFrame(missing_in_json, columns=['PDF文件名'])
    
    # 生成带时间戳的Excel文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_filename = f'title_verification_results.xlsx'
    
    # 创建Excel writer对象
    with pd.ExcelWriter(excel_filename) as writer:
        exact_matches_df.to_excel(writer, sheet_name='完全匹配', index=False)
        fuzzy_matches_df.to_excel(writer, sheet_name='模糊匹配', index=False)
        missing_in_pdf_df.to_excel(writer, sheet_name='仅在JSON中存在', index=False)
        missing_in_json_df.to_excel(writer, sheet_name='仅在PDF中存在', index=False)
        
        # 添加统计信息sheet
        stats_data = {
            '类型': ['完全匹配数量', '模糊匹配数量', 'JSON中独有数量', 'PDF中独有数量'],
            '数量': [len(matched), len(fuzzy_matched), len(missing_in_pdf), len(missing_in_json)]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='统计信息', index=False)
    
    print(f"\nResults have been saved to {excel_filename}")
    
    # 输出结果
    print("\n=== 完全匹配的标题 ===")
    for title, pdf in matched:
        print(f"✓ JSON标题: {title}")
        print(f"  PDF文件: {pdf}")
        print()
    
    print("\n=== 模糊匹配的标题 ===")
    for title, pdf, similarity in fuzzy_matched:
        print(f"? JSON标题: {title}")
        print(f"  PDF文件: {pdf}")
        print(f"  相似度: {similarity:.2%}")
        print()
    
    print("\n=== JSON中有但PDF文件夹中没有的标题 ===")
    for title in missing_in_pdf:
        print(f"✗ {title}")
    
    print("\n=== PDF文件夹中有但JSON中没有的文件 ===")
    for filename in missing_in_json:
        print(f"✗ {filename}")
    
    # 输出统计信息
    print(f"\n总计：")
    print(f"- 完全匹配数量: {len(matched)}")
    print(f"- 模糊匹配数量: {len(fuzzy_matched)}")
    print(f"- JSON中有但PDF中没有的数量: {len(missing_in_pdf)}")
    print(f"- PDF中有但JSON中没有的数量: {len(missing_in_json)}")

def score_similarity(str1, str2):
    """计算两个字符串的相似度"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()

if __name__ == "__main__":
    # 这里填入你的JSON文件路径和PDF文件夹路径
    json_path = "./HCM/4.7+4.8/HCM4.8.json"
    pdf_folder = "./HCM/4.7+4.8/4.7和4.8合并去重"
    
    verify_titles(json_path, pdf_folder) 