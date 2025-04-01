import pandas as pd

def process_references(df):
    # 创建一个新的 DataFrame 来存储处理后的结果
    processed_df = []
    
    # 期望的下一个参考文献编号
    expected_number = 1
    
    # 上一行的索引，用于合并操作
    prev_index = None
    
    for index, row in df.iterrows():
        current_number = row['Reference_Number']
        
        try:
            # 尝试将 reference_number 转换为整数
            num = int(current_number)
            
            # 检查是否符合递增序列
            if num == expected_number:
                # 符合序列，正常添加这一行
                processed_df.append(row.to_dict())
                prev_index = len(processed_df) - 1
                expected_number += 1
            else:
                # 不符合序列，需要合并到上一行
                if prev_index is not None:
                    # 合并内容
                    merged_content = processed_df[prev_index]['Content'] + ' ' + \
                                   str(current_number) + ' ' + str(row['Content'])
                    processed_df[prev_index]['Content'] = merged_content
                else:
                    # 如果是第一行就出现异常，直接添加
                    processed_df.append(row.to_dict())
                    prev_index = len(processed_df) - 1
                    expected_number += 1
                    
        except ValueError:
            # reference_number 不能转换为整数，视为需要合并的情况
            if prev_index is not None:
                merged_content = processed_df[prev_index]['Content'] + ' ' + \
                               str(current_number) + ' ' + str(row['Content'])
                processed_df[prev_index]['Content'] = merged_content
            else:
                processed_df.append(row.to_dict())
                prev_index = len(processed_df) - 1
    
    # 转换回 DataFrame
    return pd.DataFrame(processed_df)

# 使用示例：
df = pd.read_excel('61.xlsx')  # 读取你的数据文件
processed_df = process_references(df)
processed_df.to_excel('processed_file.xlsx', index=False)  # 保存处理后的文件