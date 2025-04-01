import PyPDF2
import re
import pandas as pd
from pathlib import Path

def extract_references(pdf_path, start_page=76, end_page=77):
    """
    从PDF文件中提取参考文献
    Args:
        pdf_path: PDF文件路径
        start_page: 开始页码
        end_page: 结束页码
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
        
        # 添加更详细的调试打印
        print("="*50)
        print("提取的文本前200个字符：")
        print(text[:200])
        print("="*50)
        print("文本总长度：", len(text))
        print("="*50)
        
        references_text = text  # 直接使用提取的文本，因为图片显示整页都是参考文献
        
        # 简化的正则表达式，匹配 "数字 空格 内容" 的格式
        ref_pattern = r'(?:^|\s)(\d+)\s+(.*?)(?=(?:\s+\d+\s+)|$)'
        matches = re.finditer(ref_pattern, references_text, re.MULTILINE | re.DOTALL)
        
        references = []
        for match in matches:
            ref_num = match.group(1)
            ref_content = match.group(2).strip()
            # 清理内容中的多余空白字符
            ref_content = ' '.join(ref_content.split())
            
            references.append({
                'Reference_Number': int(ref_num),
                'Content': ref_content
            })
        
        # 添加调试打印
        print(f"总共找到 {len(references)} 条参考文献")
        
        # 如果没有找到参考文献，打印一些文本样本供分析
        if len(references) == 0:
            print("\n未找到参考文献，显示文本样本：")
            # 每100个字符打印一行，显示前500个字符
            for i in range(0, min(500, len(text)), 100):
                print(f"字符 {i}-{i+100}:", text[i:i+100])
        
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
    pdf_path = 'breast_cancer/BreastCancer_2025.V1_EN.pdf'
    output_path = "76.xlsx"
    
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
