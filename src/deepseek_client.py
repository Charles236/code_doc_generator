# main.py  

import os  
import openai  
from dotenv import load_dotenv  

# --- 配置 ---  
# 从.env文件加载环境变量  
load_dotenv()  

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  
# DeepSeek提供兼容OpenAI的API，需将base_url设置为DeepSeek的端点。  
# 根据最新信息，具体URL可能为https://api.deepseek.com或https://api.deepseek.com/v1  
# 请从DeepSeek官方文档确认正确的base URL。  
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"  # 或"https://api.deepseek.com" - 需验证！  

# --- 初始化函数 ---  
def initialize_deepseek_client():  
    """  
    初始化并返回DeepSeek API客户端。  
    """  
    if not DEEPSEEK_API_KEY:  
        raise ValueError("未在环境变量中找到DEEPSEEK_API_KEY。"  
                         "请在.env文件或系统环境中设置。")  

    try:  
        client = openai.OpenAI(  
            api_key=DEEPSEEK_API_KEY,  
            base_url=DEEPSEEK_BASE_URL  
        )  
        print("DeepSeek客户端初始化成功。")  
        # 可在此处添加简单测试调用（如列出模型，若支持）  
        # 或低成本API调用来确保连接性。  
        # 示例：尝试列出模型（实际端点可能不同或不支持）：  
        # models = client.models.list()  
        # print("可用模型（示例）:", models.data[0].id if models.data else "未找到模型")  
        return client  
    except Exception as e:  
        print(f"初始化DeepSeek客户端时出错：{e}")  
        return None  

# --- 主执行（示例用法） ---  
if __name__ == "__main__":  
    print("--- 步骤1：环境设置和工具选择（DeepSeek API） ---")  

    # 尝试初始化客户端  
    deepseek_client = initialize_deepseek_client()  

    if deepseek_client:  
        print("\n设置似乎成功。")  
        print("现在可以使用'deepseek_client'向DeepSeek发起API调用。")  
        print(f"使用的API密钥：{'*' * (len(DEEPSEEK_API_KEY) - 4) + DEEPSEEK_API_KEY[-4:] if DEEPSEEK_API_KEY else '未设置'}")  
        print(f"使用的基础URL：{DEEPSEEK_BASE_URL}")  

        # 向DeepSeek模型发起测试调用的占位符（如编码模型）  
        # 需使用DeepSeek提供的正确模型名称，例如"deepseek-coder"  
        # 这仅是概念性测试，需根据实际API行为调整。  
        try:  
            # 示例：基于聊天补全的概念性测试  
            # 请根据DeepSeek文档将"deepseek-coder"替换为实际模型ID  
            print("\n尝试发起测试API调用（概念性）...")  
            chat_completion = deepseek_client.chat.completions.create(  
                messages=[  
                    {  
                        "role": "user",  
                        "content": "用一句话解释什么是Python虚拟环境。"  
                    }  
                ],  
                model="deepseek-coder",  # 若更适合通用查询，可改用"deepseek-chat"  
                max_tokens=50,  
                temperature=0.7,  
            )  
            print("测试API调用成功！")  
            print(f"测试响应：{chat_completion.choices[0].message.content.strip()}")  
        except openai.APIConnectionError as e:  
            print(f"API连接错误：{e}")  
            print("请确保DEEPSEEK_BASE_URL正确且API服务可访问。")  
        except openai.AuthenticationError as e:  
            print(f"API认证错误：{e}")  
            print("请确保DEEPSEEK_API_KEY正确。")  
        except openai.RateLimitError as e:  
            print(f"API速率限制错误：{e}")  
        except openai.NotFoundError as e:  
            print(f"API未找到错误（检查模型名称或基础URL）：{e}")  
        except Exception as e:  
            print(f"测试API调用时发生意外错误：{e}")  
    else:  
        print("\n设置失败。请检查错误消息和配置。")  

    print("\n--- 步骤1结束 ---")  