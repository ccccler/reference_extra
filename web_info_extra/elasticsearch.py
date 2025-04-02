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
    excel_path = 'chinese_raw/CSCO_乳腺癌诊疗指南2023.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    
    # 创建新的列来存储所有字段
    new_columns = {
        'pubmed_id': '',
        'es_title': '',
        'es_abstract': '',
        # 'es_source_id': '',
        'es_journal': '',
        'es_doi': '',
        # 'es_full_source': ''  # 保存完整的_source以备查看
    }
    
    # 添加新列
    for col in new_columns:
        df[col] = new_columns[col]
    
    # 对每个标题进行搜索
    for index, row in df.iterrows():
        title = row['title']  # 请确保这里的'Title'与你的Excel列名一致
        print(f"\n搜索标题: {title}")
        try:
            results = search_elasticsearch(title)
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
    
    # 保存更新后的Excel文件
    output_path = 'chinese_raw/CSCO_乳腺癌诊疗指南2023_elasticsearch.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()
