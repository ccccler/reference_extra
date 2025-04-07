import pandas as pd
import requests
import json

def search_elasticsearch(title):
    # Elasticsearch服务器地址
    url = "http://10.1.1.62:9200/literature_index_v3/_search"
    
    # 请求头
    headers = {
        "Content-Type": "application/json"
    }
    
    # 查询体
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "title": title
                        }
                    }
                ]
            }
        },
        "size": 2
    }
    
    # 发送POST请求
    response = requests.post(url, headers=headers, json=query)
    
    return response.json()

def main():
    # 读取Excel文件
    # 请替换 'your_excel.xlsx' 为你的Excel文件名
    # 'Sheet1' 为工作表名
    # 'Title' 为列名
    excel_path = 'test.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    
    # 创建一个列表来存储所有搜索结果
    all_results = []
    
    # 对每个标题进行搜索
    for index, row in df.iterrows():
        title = row['title']
        print(f"\n搜索标题: {title}")
        try:
            results = search_elasticsearch(title)
            # 将每个搜索结果添加到列表中，同时保存原始标题
            result_entry = {
                'original_title': title,
                'search_results': results
            }
            all_results.append(result_entry)
            
            # 检查是否有搜索结果
            if results['hits']['hits']:
                # 获取第一个匹配结果
                first_hit = results['hits']['hits'][0]
                source = first_hit['_source']
                
                # 更新各个字段
                df.at[index, 'pubmed_id'] = first_hit['_id']
                df.at[index, 'es_title'] = source.get('title', '')
                df.at[index, 'es_abstract'] = source.get('abstract', '')
                # df.at[index, 'es_source_id'] = source.get('source_id', '')
                df.at[index, 'es_journal'] = source.get('journal', '')
                df.at[index, 'es_doi'] = source.get('doi', '')
                # 保存完整的_source
                # df.at[index, 'es_full_source'] = json.dumps(source, ensure_ascii=False)
            else:
                print(f"未找到匹配结果: {title}")
        except Exception as e:
            print(f"搜索出错: {str(e)}")
    
    # 保存所有搜索结果到JSON文件
    json_output_path = 'search_results.json'
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nJSON结果已保存到: {json_output_path}")
    
    # 保存更新后的Excel文件
    output_path = 'test_output.xlsx'
    df.to_excel(output_path, index=False)
    print(f"Excel结果已保存到: {output_path}")

if __name__ == "__main__":
    main()
