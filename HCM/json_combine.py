import json

def combine_json_files(file1_path, file2_path, output_path):
    # 读取第一个JSON文件
    with open(file1_path, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)
    
    # 读取第二个JSON文件
    with open(file2_path, 'r', encoding='utf-8') as f2:
        data2 = json.load(f2)
    
    # 用于存储所有标题
    titles = set()
    # 用于存储重复的标题
    duplicates = set()
    # 合并后的结果
    combined_data = []
    
    # 处理第一个文件的数据
    for item in data1:
        if 'Title' in item:
            if item['Title'] in titles:
                duplicates.add(item['Title'])
            else:
                titles.add(item['Title'])
                combined_data.append(item)
    
    # 处理第二个文件的数据
    for item in data2:
        if 'Title' in item:
            if item['Title'] in titles:
                duplicates.add(item['Title'])
            else:
                titles.add(item['Title'])
                combined_data.append(item)
    
    # 将合并后的数据写入新文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
    
    # 返回重复的标题列表
    return list(duplicates)

if __name__ == "__main__":
    # 使用示例
    file1_path = "./HCM/4.7+4.8/HCM4.7.json"  # 第一个JSON文件路径
    file2_path = "./HCM/4.7+4.8/HCM4.8.json"  # 第二个JSON文件路径
    output_path = "./HCM/4.7+4.8/HCM4.7+4.8.json"  # 输出文件路径
    
    duplicates = combine_json_files(file1_path, file2_path, output_path)
    
    # 打印重复的标题
    if duplicates:
        print("发现以下重复的标题：")
        for title in duplicates:
            print(f"- {title}")
    else:
        print("没有发现重复的标题") 