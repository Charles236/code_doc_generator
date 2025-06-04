# src/doc_generator.py

import time
from typing import List, Dict, Any, Optional

# DeepSeek API调用配置
# 如果需要，可以将这些配置设为可自定义参数
DEEPSEEK_MODEL_NAME = "deepseek-coder"  # 根据任务效果，也可选择"deepseek-chat"
MAX_TOKENS_EXPLANATION = 500
MAX_TOKENS_DOCSTRING = 300
TEMPERATURE = 0.5  # 调整此值可控制输出的创造性程度（值越低越确定）
API_CALL_DELAY_SECONDS = 2  # API调用间隔时间，避免触发限流

def _make_api_call(client: Any, messages: List[Dict[str, str]], max_tokens: int) -> Optional[str]:
    """
    调用DeepSeek API的辅助函数
    """
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"    [!] API调用错误: {e}")
        # 可添加更具体的错误处理（例如处理限流、认证错误等）
        return None

def generate_explanation_for_element(client: Any, code_element: Dict[str, Any]) -> Optional[str]:
    """
    为给定的代码元素生成纯文本解释
    """
    element_type = code_element['type']
    element_name = code_element['name']
    element_code = code_element['code']
    class_name = code_element.get('class_name')

    prompt_intro = f"你是一位擅长代码分析和文档编写的专家AI助手。"
    
    user_prompt = f"解释以下名为'{element_name}'的Python {element_type}"
    if class_name:
        user_prompt += f"（属于'{class_name}'类）"
    user_prompt += f"的功能。代码如下：\n\n```python\n{element_code}\n```\n\n"
    user_prompt += "请用清晰简洁的语言进行解释。重点说明其目的、输入、输出（如果有）以及主要行为。"

    messages = [
        {"role": "system", "content": prompt_intro},
        {"role": "user", "content": user_prompt}
    ]

    print(f"  -> 正在为{element_type} '{element_name}'生成解释...")
    explanation = _make_api_call(client, messages, MAX_TOKENS_EXPLANATION)
    
    if explanation:
        print(f"  <- 已收到'{element_name}'的解释。")
    else:
        print(f"  <!> 未能为'{element_name}'生成解释。")
    return explanation

def generate_docstring_for_element(client: Any, code_element: Dict[str, Any]) -> Optional[str]:
    """
    为给定的代码元素生成Google风格的文档字符串
    """
    element_type = code_element['type']
    element_name = code_element['name']
    element_code = code_element['code']
    class_name = code_element.get('class_name')

    prompt_intro = f"你是一位擅长生成高质量代码文档的专家AI助手。"
    
    user_prompt = f"为以下名为'{element_name}'的Python {element_type}"
    if class_name:
        user_prompt += f"（来自'{class_name}'类）"
    user_prompt += f"生成简洁的Google风格文档字符串。代码如下：\n\n```python\n{element_code}\n```\n\n"
    user_prompt += "文档字符串应准确描述其用途、参数（如果有，包括可推断的类型）、"
    user_prompt += "以及返回值（如果有，包括可推断的类型）。对于类，提供简要概述，"
    user_prompt += "并在概述中提及关键属性或方法（如适用）。不要在文档字符串主体中包含函数/方法/类签名，只包含描述性文本。"
    user_prompt += "确保文档字符串以简短的摘要行开头，后跟空行，然后根据需要添加更详细的说明。正确格式化以符合Python规范。"

    messages = [
        {"role": "system", "content": prompt_intro},
        {"role": "user", "content": user_prompt}
    ]

    print(f"  -> 正在为{element_type} '{element_name}'生成文档字符串...")
    docstring = _make_api_call(client, messages, MAX_TOKENS_DOCSTRING)
    
    if docstring:
        # 清理LLM可能生成的多余markdown ```python ``` 代码块标记
        if docstring.startswith("```python\n"):
            docstring = docstring.replace("```python\n", "", 1)
            if docstring.endswith("\n```"):
                docstring = docstring[:-len("\n```")]
        if docstring.startswith("```"):  # 通用的 ```
            docstring = docstring.replace("```", "", 1)
            if docstring.endswith("```"):
                docstring = docstring[:-len("```")]

        # 移除LLM可能生成的多余的开头/结尾三引号
        docstring = docstring.strip().strip('"""').strip("'''").strip()
        print(f"  <- 已收到'{element_name}'的文档字符串。")
    else:
        print(f"  <!> 未能为'{element_name}'生成文档字符串。")
    return docstring

def generate_project_overview(client: Any, all_elements: List[Dict[str, Any]], project_name: str = "本项目") -> Optional[str]:
    """
    为README文件生成项目的高层概述
    """
    if not all_elements:
        return "未提供代码元素，无法生成概述。"

    summaries = []
    for element in all_elements:
        if element.get('explanation'):  # 使用之前生成的解释
            summary = f"- {element['type'].capitalize()} '{element['name']}': {element['explanation'][:150]}..."  # 截断以保持简洁
            if element.get('class_name'):
                summary = f"- {element['type'].capitalize()} '{element['name']}' (在'{element['class_name']}'类中): {element['explanation'][:150]}..."
            summaries.append(summary)
        elif element['type'] == 'class':  # 如果没有解释，使用类名
            summaries.append(f"- 类 '{element['name']}'")

    if not summaries:
        return "没有可用的解释来生成概述。"

    prompt_intro = "你是一个负责为README文件创建项目摘要的AI助手。"
    user_prompt = (
        f"根据以下来自'{project_name}'的代码元素摘要，"
        f"生成适合项目README文件的简洁、高层概述（2-4段）。"
        f"概述应描述项目的主要目的和可从这些元素推断出的关键功能。\n\n"
        f"代码元素摘要:\n" + "\n".join(summaries[:20]) +  # 限制输入大小
        f"\n\n专注于描述项目可能的连贯叙述。"
    )
    
    messages = [
        {"role": "system", "content": prompt_intro},
        {"role": "user", "content": user_prompt}
    ]

    print(f"  -> 正在为'{project_name}'生成项目概述...")
    overview = _make_api_call(client, messages, max_tokens=600)
    if overview:
        print(f"  <- 已收到项目概述。")
    else:
        print(f"  <!> 未能生成项目概述。")
    return overview

def process_elements_for_docs(client: Any, code_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    遍历代码元素，为每个元素生成解释和文档字符串。
    通过添加'explanation'和'docstring'键来修改输入的字典列表。
    """
    print(f"\n开始为{len(code_elements)}个元素生成文档...")
    for i, element in enumerate(code_elements):
        print(f"\n处理元素 {i+1}/{len(code_elements)}: {element['type']} '{element['name']}' 在 '{element['file_path']}'")
        
        # 过滤掉可能不需要详细解释/文档字符串的元素（例如非常短的元素）
        # 或基于类型过滤（例如，如果不想为类本身生成文档，只处理其方法）
        # 目前，我们处理所有函数、方法和类。
        if element['type'] in ['function', 'method', 'async function', 'async method', 'class']:
            explanation = generate_explanation_for_element(client, element)
            element['explanation'] = explanation
            time.sleep(API_CALL_DELAY_SECONDS)  # 遵守API速率限制

            docstring = generate_docstring_for_element(client, element)
            element['docstring'] = docstring
            time.sleep(API_CALL_DELAY_SECONDS)  # 遵守API速率限制
        else:
            element['explanation'] = None
            element['docstring'] = None
            print(f"  跳过为元素类型 {element['type']} 生成文档")
            
    return code_elements