import re
import pandas as pd

def extract_references(input_file):
    # 读取MD文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到References部分
    if '## References' in content:
        content = content.split('## References')[1]
    
    # 存储提取的引用信息
    references = []
    current_id = 1
    
    # 使用正则表达式找到所有引用块
    # 每个引用块以作者开始（包含 ∙），到下一个类似的作者行之前
    reference_pattern = r'((?:[\w\s,\.]+\s*∙\s*[\w\s,\.]+\s*∙?\s*\.{3}.*?)(?=(?:\n[\w\s,\.]+\s*∙\s*[\w\s,\.]+\s*∙?\s*\.{3})|$))'
    reference_blocks = re.findall(reference_pattern, content, re.DOTALL)
    
    print(f"找到 {len(reference_blocks)} 个引用块")  # 调试输出
    
    for block in reference_blocks:
        try:
            # 提取作者（第一行，包含 ∙ 和 ... 的内容）
            authors = re.search(r'^(.*?\.{3})', block, re.MULTILINE)
            if not authors:
                continue
            authors = authors.group(1).strip()
            
            # 提取标题（在**之间的内容）
            title = re.search(r'\*\*(.*?)\*\*', block)
            if not title:
                continue
            title = title.group(1).strip()
            
            # 提取期刊名称（在单个*之间的内容）
            journal = re.search(r'\*((?:[^*]|\*\*)*?)\.\*', block)
            if not journal:
                continue
            journal = journal.group(1).strip()
            
            # 提取年份和卷号信息
            year = re.search(r'(\d{4})', block)
            year = year.group(1) if year else ""
            
            # 提取DOI或URL
            link = ""
            doi_match = re.search(r'\[Crossref\]\((.*?)\)', block)
            url_match = re.search(r'\[Full Text.*?\]\((.*?)\)', block)
            if doi_match:
                link = doi_match.group(1)
            elif url_match:
                link = url_match.group(1)
            
            # 添加到引用列表
            reference = {
                'ID': current_id,
                'Authors': authors,
                'Title': title,
                'Journal': journal,
                'Year': year,
                'DOI/URL': link
            }
            
            references.append(reference)
            print(f"成功处理引用 {current_id}:", reference)  # 调试输出
            current_id += 1
            
        except Exception as e:
            print(f"处理块时出错: {e}")  # 调试输出
            print(f"问题块内容:\n{block}")  # 调试输出
            continue
    
    # 创建DataFrame
    df = pd.DataFrame(references)
    
    # 保存为Excel文件
    if not references:
        print("警告：没有找到任何引用")
    else:
        print(f"总共提取了 {len(references)} 条引用")
        df.to_excel('references.xlsx', index=False)
        print("已保存到 references.xlsx")
        
        # 显示提取的内容预览
        print("\n提取的内容预览：")
        print(df)

def extract_bold_titles_and_authors(input_file):
    # 读取MD文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 将内容按行分割，以便获取上下文
    lines = content.split('\n')
    total_lines = len(lines)
    
    # 创建一个包含所有信息的列表字典
    data = []
    
    # 遍历每一行
    for i in range(total_lines):
        # 查找当前行是否包含加粗文本
        title_match = re.search(r'\*\*(.*?)\*\*', lines[i])
        if title_match:
            title = title_match.group(1).strip()
            # 跳过纯数字的加粗文本
            if title.isdigit():
                continue
                
            # 获取标题上两行的作者信息
            authors = ""
            if i >= 2:
                authors = lines[i-2].strip()
            
            # 获取标题下两行的期刊信息
            journal = ""
            if i + 2 < total_lines:
                journal = lines[i+2].strip()
                # 移除期刊信息中的斜体标记 *
                journal = journal.replace('*', '').strip()
            
            # 获取标题下四行的URL信息
            url = ""
            if i + 4 < total_lines:
                url_line = lines[i+4].strip()
                # 提取URL（在方括号和圆括号之间的内容）
                url_match = re.search(r'\[(.*?)\]\((.*?)\)', url_line)
                if url_match:
                    url = url_match.group(2).strip()
            
            # 查找PubMed链接（在标题后的10行内查找）
            pubmed_url = ""
            for j in range(i + 1, min(i + 18, total_lines)):
                if lines[j].strip().startswith('[PubMed]'):
                    pubmed_match = re.search(r'\[PubMed\]\((.*?)\)', lines[j])
                    if pubmed_match:
                        pubmed_url = pubmed_match.group(1).strip()
                    break
            
            data.append({
                'ID': len(data) + 1,
                'Authors': authors,
                'Title': title,
                'Journal': journal,
                'URL': url,
                'PubMed': pubmed_url
            })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存为Excel文件
    df.to_excel('paper_info.xlsx', index=False)
    
    # 打印找到的所有信息
    print("找到的论文信息：")
    for row in data:
        print(f"{row['ID']}.")
        print(f"作者: {row['Authors']}")
        print(f"标题: {row['Title']}")
        print(f"期刊: {row['Journal']}")
        print(f"URL: {row['URL']}")
        print(f"PubMed: {row['PubMed']}\n")
    
    print("\n信息已保存到 paper_info.xlsx")
    
    return data

if __name__ == "__main__":
    input_file = "annals_of_oncology/input.md"
    data = extract_bold_titles_and_authors(input_file)