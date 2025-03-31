import PyPDF2
import re
import pandas as pd
from pathlib import Path

def extract_references(pdf_path, start_page=61, end_page=62):
    """
    从PDF文件中提取参考文献
    Args:
        pdf_path: PDF文件路径
        start_page: 开始页码（默认83）
        end_page: 结束页码（默认None，表示读到最后一页）
    """
    # 打开PDF文件
    with open(pdf_path, 'rb') as file:
        # 创建PDF读取器对象
        pdf_reader = PyPDF2.PdfReader(file)
        
        # 如果没有指定结束页码，设置为最后一页
        if end_page is None:
            end_page = len(pdf_reader.pages)
        
        # 确保页码范围有效
        start_page = max(1, min(start_page, len(pdf_reader.pages)))
        end_page = max(start_page, min(end_page, len(pdf_reader.pages)))
        
        # 存储所有文本
        text = ""
        
        # 从指定页码开始读取到结束页码
        for page_num in range(start_page - 1, end_page):
            text += pdf_reader.pages[page_num].extract_text()
        
        # 查找References部分
        references_match = re.search(r'References\s*(.*?)(?=\n\n|$)', text, re.DOTALL)
        if not references_match:
            return []
        
        references_text = references_match.group(1)
        
        # 新的正则表达式模式：
        # (?:^|\n)\s* - 匹配行首或换行符后的空白
        # (\d+)\.\s+ - 匹配参考文献编号和后面的空白
        # ((?:(?!(?:^|\n)\s*\d+\.).)*) - 匹配直到下一个独立的编号之前的所有内容
        ref_pattern = r'(?:^|\n)\s*(\d+)\.\s+((?:(?!(?:^|\n)\s*\d+\.).)*)'
        matches = re.finditer(ref_pattern, references_text, re.DOTALL)
        
        references = []
        for match in matches:
            ref_num = match.group(1)
            ref_content = match.group(2).strip()
            
            references.append({
                'Reference_Number': int(ref_num),
                'Content': ref_content
            })
        
        return references

def save_to_excel(references, output_path):
    """
    将参考文献保存到Excel文件
    """
    df = pd.DataFrame(references)
    df.to_excel(output_path, index=False)
    print(f"参考文献已保存到: {output_path}")

def main():
    # 设置文件路径
    pdf_path = 'breast_cancer/BreastCancer_2024.V5_EN_NCCN.pdf'
    output_path = Path(pdf_path).stem + "_61_references.xlsx"
    
    # 提取参考文献
    try:
        references = extract_references(pdf_path)
        if references:
            save_to_excel(references, output_path)
        else:
            print("未找到参考文献部分")
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()
