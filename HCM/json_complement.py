import json

def merge_pdf_paths(file1_path, file2_path, output_path):
    # 读取第一个 JSON 文件
    with open(file1_path, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    
    # 读取第二个 JSON 文件
    with open(file2_path, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    
    # 创建一个字典，用 Title 作为键来存储文件1中的 pdf_path
    pdf_paths = {item['Title']: item.get('pdf_path') for item in data1}
    
    # 遍历文件2中的数据
    for item in data2:
        title = item['Title']
        # 如果在文件1中找到相同的 Title
        if title in pdf_paths and pdf_paths[title]:
            # 将 pdf_path 添加到文件2的数据中
            item['pdf_path'] = pdf_paths[title]
    
    # 将更新后的数据保存到新文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data2, f, ensure_ascii=False, indent=4)

# 使用示例
file1_path = './HCM/4.7+4.8/HCM4.8_pathrename.json'  # 第一个JSON文件的路径
file2_path = './HCM/4.7+4.8/HCM4.8完整.json'  # 第二个JSON文件的路径
output_path = 'merged_output.json'  # 输出文件的路径

merge_pdf_paths(file1_path, file2_path, output_path)
