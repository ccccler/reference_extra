import json
import pandas as pd
import os

def check_and_update_json(json_file_path, excel_file_path):
    # 读取Excel文件
    try:
        # 读取两个sheet的数据
        exact_match_df = pd.read_excel(excel_file_path, sheet_name='完全匹配')
        fuzzy_match_df = pd.read_excel(excel_file_path, sheet_name='模糊匹配')
        
        # 获取"JSON标题"列和"PDF文件名"列的对应关系（用于模糊匹配sheet）
        fuzzy_match_dict = dict(zip(
            fuzzy_match_df['JSON标题'].dropna(),
            fuzzy_match_df['PDF文件名'].dropna()
        ))
        
        # 获取所有标题
        exact_titles = set(exact_match_df['JSON标题'].dropna().tolist())
        fuzzy_titles = set(fuzzy_match_df['JSON标题'].dropna().tolist())
        all_titles = exact_titles.union(fuzzy_titles)
        
    except Exception as e:
        print(f"读取Excel文件时出错: {str(e)}")
        return
    
    # 读取JSON文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件时出错: {str(e)}")
        return
    
    # 检查并更新数据
    modified_count = 0
    pdf_renamed_count = 0
    
    for item in data:
        if 'Title' in item and 'pdf_path' in item:
            if item['Title'] not in all_titles:
                # 如果标题不在任何sheet中，将pdf_path设为空
                item['pdf_path'] = ""
                modified_count += 1
            elif item['Title'] in fuzzy_titles:
                # 如果标题在模糊匹配sheet中，更新pdf文件名
                new_pdf_name = fuzzy_match_dict.get(item['Title'])
                if new_pdf_name:
                    # 保持路径前缀不变，只更新pdf文件名
                    new_path = "./artical/4.7和4.8合并去重/" + new_pdf_name
                    if not new_path.endswith('.pdf'):
                        new_path += '.pdf'
                    item['pdf_path'] = new_path
                    pdf_renamed_count += 1
    
    # 保存更新后的JSON文件
    try:
        output_path = json_file_path.replace('.json', '_updated.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"处理完成！")
        print(f"清空pdf_path的数据数量: {modified_count}")
        print(f"更新pdf文件名的数据数量: {pdf_renamed_count}")
        print(f"更新后的文件已保存为: {output_path}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")

# 使用示例
json_file_path = './HCM/4.7+4.8/HCM4.8_terminal.json'  # 请替换为你的JSON文件路径
excel_file_path = './HCM/4.7+4.8/title_verification_results.xlsx'    # 请替换为你的Excel文件路径

check_and_update_json(json_file_path, excel_file_path)
