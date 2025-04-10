import pandas as pd
import json
from datetime import datetime

def convert_date_to_string(date_value):
    """
    将各种可能的日期格式转换为字符串
    """
    if pd.isna(date_value):  # 处理空值
        return ''
    
    try:
        # 如果是datetime类型
        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.strftime('%Y-%m-%d')
        
        # 如果是字符串类型，尝试解析然后格式化
        if isinstance(date_value, str):
            # 尝试解析不同的日期格式
            try:
                parsed_date = pd.to_datetime(date_value)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                # 如果无法解析，返回原始字符串
                return date_value
        
        # 如果是数值类型（可能是Excel的序列号）
        if isinstance(date_value, (int, float)):
            try:
                # 将Excel日期序列号转换为datetime
                date_datetime = pd.to_datetime('1899-12-30') + pd.Timedelta(days=int(date_value))
                return date_datetime.strftime('%Y-%m-%d')
            except:
                return str(date_value)
        
        # 其他情况，转换为字符串
        return str(date_value)
    
    except Exception as e:
        print(f"日期转换错误: {str(e)}, 值: {date_value}")
        return str(date_value)

def match_and_update_json(json_file_path, excel_file_path, output_json_path):
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 读取Excel文件，不自动转换日期
    df = pd.read_excel(excel_file_path)
    
    # 创建一个字典，用Title作为键来快速查找Excel中的数据
    excel_dict = df.set_index('Title').to_dict('index')
    
    # 遍历JSON数据并更新
    for item in json_data:
        if 'Title' in item:
            title = item['Title']
            if title in excel_dict:
                # 从Excel中获取对应的数据
                excel_row = excel_dict[title]
                
                # 更新JSON数据
                item['Item Type'] = str(excel_row.get('Item Type', ''))
                item['ISSN'] = str(excel_row.get('ISSN', ''))
                # 特殊处理日期字段
                item['Date'] = convert_date_to_string(excel_row.get('Date', ''))
                # 转换Issue和Volume为字符串
                item['Issue'] = str(excel_row.get('Issue', ''))
                item['Volume'] = str(excel_row.get('Volume', ''))
    
    # 保存更新后的JSON文件
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

def main():
    # 设置文件路径
    json_file_path = './HCM/4.7+4.8/HCM4.8.json'  # 输入JSON文件路径
    excel_file_path = './HCM/4.7+4.8/HCM4.8全集.xlsx'  # Excel文件路径
    output_json_path = './HCM/4.7+4.8/HCM4.8补充.json'  # 输出JSON文件路径
    
    try:
        match_and_update_json(json_file_path, excel_file_path, output_json_path)
        print("数据匹配和更新完成！")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == '__main__':
    main()
