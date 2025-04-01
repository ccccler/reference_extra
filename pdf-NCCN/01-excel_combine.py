import pandas as pd
import os

def combine_excel_files(folder_path, output_file='combined_excel.xlsx'):
    # 存储所有数据框的列表
    all_dataframes = []
    
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 检查文件是否是Excel文件
        if file.endswith(('.xlsx', '.xls')):
            file_path = os.path.join(folder_path, file)
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)
                # 添加一列来标识来源文件
                df['Source_File'] = file
                # 将数据框添加到列表中
                all_dataframes.append(df)
                print(f"成功读取文件: {file}")
            except Exception as e:
                print(f"处理文件 {file} 时出错: {str(e)}")
    
    if not all_dataframes:
        print("没有找到Excel文件")
        return
    
    # 合并所有数据框
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # 保存合并后的文件
    output_path = os.path.join(folder_path, output_file)
    combined_df.to_excel(output_path, index=False)
    print(f"合并完成！文件已保存为: {output_file}")

# 使用示例
if __name__ == "__main__":
    # 替换为你的文件夹路径
    folder_path = "NCCN_2024v5"
    combine_excel_files(folder_path)
