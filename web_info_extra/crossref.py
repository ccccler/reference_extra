import requests
import json
import pandas as pd

# 读取Excel文件
df = pd.read_excel('lacent.xlsx')

def search_crossref(row):
    """
    使用Excel中的一行数据搜索Crossref
    """
    # 基础 URL
    base_url = "https://api.crossref.org/works"
    
    # 设置查询参数，使用Excel中的数据
    params = {
        "query.bibliographic": f'"{row["title"]}"',
        "filter": f"from-pub-date:{row['year']},until-pub-date:{row['year']},type:journal-article,container-title:{row['journal_all']}",
        "select": "DOI,title,abstract,URL",
        "rows": 1,
        "sort": "score",
        "order": "desc",
        "mailto": "your-email@example.com"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # 只处理需要的字段
        if data['message']['items']:
            item = data['message']['items'][0]
            return {
                "Crossref_Title": item.get('title', [''])[0],
                "Crossref_DOI": item.get('DOI', ''),
                "Crossref_Abstract": item.get('abstract', ''),
                "Crossref_URL": item.get('URL', 'No URL available')
            }
    return {
        "Crossref_Title": '',
        "Crossref_DOI": '',
        "Crossref_Abstract": '',
        "Crossref_URL": ''
    }

# 对Excel中的每一行进行处理
for index, row in df.iterrows():
    print(f"Processing row {index + 1}...")
    result = search_crossref(row)
    
    # 将结果直接添加到原DataFrame的对应行
    for key, value in result.items():
        df.at[index, key] = value
    
    print(f"Processed DOI: {result['Crossref_DOI'] or 'Not found'}")
    print("-" * 50)

# 保存回原Excel文件
df.to_excel('lacent_crossref.xlsx', index=False)
print("\nResults have been added to the original Excel file")