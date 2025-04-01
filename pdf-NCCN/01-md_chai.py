import re

def split_text_blocks(text):
    # 使用正则表达式匹配[数字]模式
    pattern = r'(\[\d+\])'
    
    # 先用正则表达式分割文本
    blocks = re.split(pattern, text)
    
    # 初始化结果列表
    result = []
    current_block = ''
    
    # 处理分割后的文本块
    for i, block in enumerate(blocks):
        # 如果匹配到[数字]模式
        if re.match(r'\[\d+\]', block):
            # 如果当前块不为空白字符才添加到结果中
            if current_block.strip():
                result.append(current_block.strip())
            # 开始新的文本块，保留[数字]标记
            current_block = block
        else:
            current_block += block
    
    # 添加最后一个文本块（确保不为空）
    if current_block.strip():
        result.append(current_block.strip())
    
    # 过滤掉空文本块
    result = [block for block in result if block.strip()]
    
    return result

# 示例使用
def process_md_file(file_path):
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            text_blocks = split_text_blocks(content)
            
            # 将文本块重新组合，每个块之间只添加一个换行符
            processed_content = '\n'.join(text_blocks)
            
            # 将处理后的内容写回原文件
            with open(file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(processed_content)
            
            # 打印处理信息
            print(f"文件已处理完成，共分割为 {len(text_blocks)} 个文本块")
            print(f"处理结果已保存到: {file_path}")
            
            return text_blocks
            
    except FileNotFoundError:
        print(f"找不到文件: {file_path}")
        return []
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")
        return []

# 使用示例
file_path = "./Chinese_pre/caca指南.md"
text_blocks = process_md_file(file_path)
