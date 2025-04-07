import aiohttp
import asyncio
import json
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BackgroundProcessor:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.api_key = api_key
        self.results = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def call_api_sse(self, background: str, idx: int) -> Dict:
        """使用SSE方式调用API"""
        url = 'http://192.168.1.90:5000/v1/completion-messages'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 修改提示词模板
        prompt = f"""# 你是一个医学论文提取助手，请从医学论文摘要的背景（目的）中提取出研究内容关键词。
        背景（目的）部分提供了研究的背景信息，阐述了该研究的动机和重要性。它通常包括相关领域的现有知识、问题的定义、研究的不足或知识空白，以及研究为何重要。
        你的目标是提取以上这些领域的关键词汇。要求你返回相关领域的术语，例如疾病的类型、症状的分类、研究的空白等。
        关键词以英文反馈，要求以json格式输出，注意，只允许返回json格式，不要输出其他内容。  
        
        # 请按照以下json格式输出分析结果：
        {{
            "BG_term1": "", 
            "BG_term2": "",  
            "BG_term3": "",
            ......
        }}

        # 研究背景（目的）：{background}
        """

        data = {
            "inputs": {"query": prompt},
            "response_mode": "blocking",
            "user": "background_processor"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, json=data, timeout=None) as response:
                    if response.status != 200:
                        raise Exception(f"API返回错误状态码: {response.status}")
                    
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                        model_response = response_data.get('answer', '')
                        print(f"✓ 完成第 {idx+1} 条背景信息处理")

                        return {
                            "id": idx,
                            "original_background": background,
                            "model_response": model_response.strip()
                        }
                    except json.JSONDecodeError as e:
                        raise Exception(f"JSON解析错误: {e}")

        except Exception as e:
            print(f"✗ 第 {idx+1} 条背景信息处理失败: {str(e)}")
            return {
                "id": idx,
                "original_background": background,
                "model_response": f"ERROR: {str(e)}"
            }

    async def process_background(self, background: str, idx: int) -> Dict:
        """处理单条背景信息"""
        async with self.semaphore:
            await asyncio.sleep(0.1)
            return await self.call_api_sse(background, idx)

    async def process_all_backgrounds(self, backgrounds: List[str]):
        """处理所有背景信息"""
        tasks = [self.process_background(bg, idx) for idx, bg in enumerate(backgrounds)]
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理可能的异常
        self.results = [
            result if not isinstance(result, Exception)
            else {"id": idx, "original_background": backgrounds[idx], "model_response": f"ERROR: {str(result)}"}
            for idx, result in enumerate(self.results)
        ]
        
        print(f"\n全部处理完成！共处理 {len(backgrounds)} 条背景信息")

    def save_to_excel(self, output_file: str):
        """将结果保存到Excel文件"""
        df = pd.DataFrame(self.results)
        df = df[['id', 'original_background', 'model_response']]
        df.to_excel(output_file, index=False)

async def main():
    # 读取JSON文件并提取Background/Purpose字段
    with open('test_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    backgrounds = [item.get('Background/Purpose', '') for item in data]  # 修改字段名

    # 初始化处理器
    processor = BackgroundProcessor(api_key="app-0vDNiDJUUz7usGZqLn9L1moo", max_concurrent=10)
    
    # 处理所有背景信息
    await processor.process_all_backgrounds(backgrounds)
    
    # 生成输出文件名
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"bg_background_analysis.xlsx"
    
    # 保存结果
    processor.save_to_excel(output_file)
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
