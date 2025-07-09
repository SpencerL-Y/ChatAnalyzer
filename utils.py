import os

def load_api_key():
    """从本地文件读取API密钥"""
    key_file_paths = [
        os.path.join(os.getcwd(), '.secrete_api_key'),  # 工作目录下
        os.path.join(os.path.dirname(__file__), '.secrete_api_key'),  # 脚本同目录下
        os.path.join(os.path.expanduser('~'), '.llm_api_key'),   # 用户主目录
    ]
    
    for key_file in key_file_paths:
        if os.path.exists(key_file):
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"Warning: 无法读取密钥文件 {key_file}: {e}")
                continue
    
    api_key = os.getenv('LLM_API_KEY')
    if api_key:
        return api_key
    
    raise FileNotFoundError(
        "未找到API密钥。请创建以下任一文件：\n"
        f"1. {key_file_paths[0]}\n"
        f"2. {key_file_paths[1]}\n"
        f"3. {key_file_paths[2]}\n"
        "或设置环境变量 LLM_API_KEY"
    )

