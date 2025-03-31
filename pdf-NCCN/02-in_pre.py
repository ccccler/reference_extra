import pandas as pd
import numpy as np
import re

class ReferenceProcessor:
    def __init__(self, file_path, target_column='Content', ref_num_column='Reference_Number', left_column='Reference_Number'):
        """
        初始化处理器
        :param file_path: Excel文件路径d
        :param target_column: 需要处理的主要内容列名
        :param ref_num_column: 引用编号列名
        :param left_column: 左侧列名
        """
        self.file_path = file_path
        self.target_column = target_column
        self.ref_num_column = ref_num_column
        self.left_column = left_column
        self.df = pd.read_excel(file_path)
        
    def merge_available_at_entries(self):
        """处理'available at'开头的条目，将其与左侧和上方单元格合并"""
        new_data = []
        previous_value = None
        rows_to_delete = []
        
        for i in range(len(self.df)):
            current_value = self.df[self.target_column].iloc[i]
            
            if pd.isna(current_value):
                new_data.append(current_value)
                previous_value = current_value
                continue
            
            if str(current_value).lower().startswith('available at'):
                left_cell_value = self.df[self.left_column].iloc[i]
                combined_value = (f"{left_cell_value} {current_value}" 
                                if not pd.isna(left_cell_value) 
                                else current_value)
                
                if previous_value is not None and not pd.isna(previous_value):
                    new_data[-1] = str(previous_value) + ' ' + str(combined_value)
                    new_data.append(pd.NA)
                    rows_to_delete.append(i)
                else:
                    new_data.append(combined_value)
            else:
                new_data.append(current_value)
            
            previous_value = current_value
            
        self.df[self.target_column] = new_data
        self.df = self.df.drop(rows_to_delete).reset_index(drop=True)
        return self

    def fix_reference_numbers(self):
        """检查并修复引用编号的序列"""
        ref_nums = self.df[self.ref_num_column].dropna().astype(int).tolist()
        expected_nums = list(range(min(ref_nums), max(ref_nums) + 1))
        missing_nums = set(expected_nums) - set(ref_nums)
        
        if missing_nums:
            new_rows = []
            for num in missing_nums:
                new_row = pd.Series(index=self.df.columns, dtype='object')
                new_row[self.ref_num_column] = num
                new_rows.append(new_row)
            
            self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
            self.df = self.df.sort_values(by=self.ref_num_column).reset_index(drop=True)
            
        return self, sorted(missing_nums) if missing_nums else []

    def clean_copyright_text(self):
        """清理版权声明文本"""
        pattern = (r"Version 2\.2024 © 20 24 National Comprehensive Cancer Network© "  # 注意末尾空格
                  r"\(NCCN©\), All rights reserved\. NCCN Guidelines® and this illustration "
                  r"may not be reproduced in any form without the express written permission "
                  r"of NCCN \. NCCN Guidelines Version 2\.2024 \n"
                  r"Breast Cancer Screening and Diagnosis[ \n]+"  # 处理多个空格和换行
                  r"MS-\d+")
        
        def clean_content(text):
            if pd.isna(text):
                return text
            return re.sub(pattern, '', str(text)).strip()
        
        self.df[self.target_column] = self.df[self.target_column].apply(clean_content)
        return self

    def process_empty_content(self):
        """处理空的content单元格"""
        for i in range(len(self.df)):
            current_content = self.df[self.target_column].iloc[i]
            current_ref_num = self.df[self.ref_num_column].iloc[i]
            
            if pd.isna(current_content) and not pd.isna(current_ref_num):
                if i > 0:
                    previous_content = self.df[self.target_column].iloc[i-1]
                    if not pd.isna(previous_content):
                        pattern = fr"{int(current_ref_num)}\."
                        match = re.search(pattern, str(previous_content))
                        if match:
                            split_point = match.start()
                            text_to_move = previous_content[split_point:].strip()
                            self.df.at[i, self.target_column] = text_to_move
                            self.df.at[i-1, self.target_column] = previous_content[:split_point].strip()
        return self

    def save_result(self, output_path=None):
        """保存处理结果"""
        if output_path is None:
            output_path = 'processed_' + self.file_path
        self.df.to_excel(output_path, index=False)
        return self

    def process_all(self):
        """执行所有处理步骤"""
        self.merge_available_at_entries()
        missing_nums = self.fix_reference_numbers()[1]
        self.clean_copyright_text()
        self.process_empty_content()
        self.save_result()
        return missing_nums

# 使用示例
if __name__ == "__main__":
    processor = ReferenceProcessor('BreastCancer_2024.V5_EN_NCCN_73_references.xlsx')
    missing_nums = processor.process_all()
    
    if missing_nums:
        print(f"已插入缺失的引用编号: {missing_nums}")
    else:
        print("引用编号序列完整，无需插入新行") 