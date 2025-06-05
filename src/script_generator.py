# src/script_generator.py
import time
from typing import List, Dict, Any, Optional

# 从 doc_generator 借用 API 调用相关的配置和函数
# 你也可以将 _make_api_call 提取到一个通用的 utils.py 模块中
# 为简单起见，我们这里可以重新定义或直接从 doc_generator 导入（如果它不引入循环依赖）
# 假设我们从 doc_generator.py 导入这些常量
# from .doc_generator import DEEPSEEK_MODEL_NAME, TEMPERATURE, API_CALL_DELAY_SECONDS

# 由于直接导入可能导致潜在的循环依赖或仅仅是想保持模块独立，我们在这里重新定义
# 或者，更好的做法是创建一个共享的 utils.py 或 config.py 来存放这些常量和通用函数
DEEPSEEK_MODEL_SCRIPT_GENERATION = "deepseek-coder" # 或者选择更适合长文本生成的模型，如 deepseek-chat
MAX_TOKENS_SCRIPT_SECTION = 700 # 根据需要调整，脚本片段可能需要更多 token
TEMPERATURE_SCRIPT = 0.6 # 可以稍微高一点以增加脚本的生动性
API_CALL_DELAY_SECONDS = 2


def _make_llm_call_for_script(client: Any, messages: List[Dict[str, str]], max_tokens: int) -> Optional[str]:
    """
    辅助函数，用于为脚本生成调用 LLM API。
    (与 doc_generator 中的 _make_api_call 类似，但可能使用不同模型或参数)
    """
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL_SCRIPT_GENERATION,
            messages=messages,
            max_tokens=max_tokens,
            temperature=TEMPERATURE_SCRIPT
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"    [!] LLM API Call Error (for script): {e}")
        return None

def generate_script_for_section(client: Any, section_data: Dict[str, Any], project_name: str, target_audience: str = "初学者") -> Optional[str]:
    """
    为教程大纲中的单个部分生成脚本。
    """
    section_type = section_data.get("section_type")
    title = section_data.get("title")
    script_prompt = ""
    system_message = f"你是一位经验丰富的技术教程编剧和内容创作者。你的任务是为编程教程视频撰写清晰、引人入胜且易于理解的旁白脚本。脚本应面向 {target_audience}。"

    print(f"\n  -> 正在为教程部分 '{title}' (类型: {section_type}) 生成脚本...")

    if section_type == "introduction":
        project_overview = section_data.get("content_source", f"{project_name} 是一个非常有用的项目。")
        script_prompt = (
            f"为名为 '{project_name}' 的项目生成一段引人入胜的视频教程开场白。\n"
            f"项目概览：{project_overview}\n"
            f"脚本应包含：\n"
            f"1. 欢迎语。\n"
            f"2. 简要介绍项目是什么，解决了什么问题。\n"
            f"3. 预告通过本教程学习者能掌握什么。\n"
            f"4. 鼓励观众继续观看。\n"
            f"请加入视觉提示，例如：[显示项目Logo]、[展示项目运行效果的快速剪辑]、[显示教程标题卡]。"
        )
    
    elif section_type == "setup":
        setup_instructions_placeholder = section_data.get("content_source", "请描述安装和配置步骤。")
        script_prompt = (
            f"为 '{project_name}' 项目的视频教程生成“环境设置与安装”部分的脚本。\n"
            f"基本要求：{setup_instructions_placeholder}\n"
            f"脚本应包含：\n"
            f"1. 需要安装哪些主要工具或库（例如，Python 版本、pip install ...）。\n"
            f"2. 如何进行基本的项目配置（例如，API密钥、环境变量等，如果适用）。\n"
            f"3. 一个简单的导入示例（如果适用）。\n"
            f"请加入视觉提示，例如：[显示命令行界面]、[高亮显示需要输入的命令]、[展示代码编辑器中的导入语句]。"
        )

    elif section_type == "core_feature_detail":
        element_name = section_data.get("element_name")
        element_type = section_data.get("element_type")
        class_name = section_data.get("element_class_name")
        code_snippet = section_data.get("code_snippet", "# 代码片段缺失")
        explanation = section_data.get("explanation", "这个功能非常重要。") # 来自步骤3的解释

        feature_name_for_prompt = f"`{class_name}.{element_name}`" if class_name else f"`{element_name}`"

        script_prompt = (
            f"为名为 '{project_name}' 的项目的视频教程中关于核心功能 '{feature_name_for_prompt}' ({element_type}) 的部分生成详细讲解脚本。\n"
            f"这是该功能的代码：\n```python\n{code_snippet}\n```\n"
            f"这是对该功能的文字解释（供你参考，请用更口语化和教学性的方式表达）：\n\"{explanation}\"\n\n"
            f"脚本应包含：\n"
            f"1. 清晰说明这个功能是做什么的，它的主要目的是什么。\n"
            f"2. （如果适用）对其重要参数进行解释。\n"
            f"3. （如果适用）解释它返回什么。\n"
            f"4. 如何在实际中使用它（可以虚构一个简单场景）。\n"
            f"5. 逐步引导观众理解代码逻辑，但避免逐行朗读代码，而是解释关键部分和整体流程。\n"
            f"请加入视觉提示，例如：[在屏幕上显示代码片段：{feature_name_for_prompt}]、[高亮代码的关键行]、[显示一个简单的调用示例]、[图示说明数据流或逻辑]。"
        )
    
    elif section_type == "conclusion":
        conclusion_placeholder = section_data.get("content_source", "总结教程内容并鼓励学习。")
        script_prompt = (
            f"为名为 '{project_name}' 的项目的视频教程生成“总结与展望”部分的脚本。\n"
            f"基本要求：{conclusion_placeholder}\n"
            f"脚本应包含：\n"
            f"1. 简要回顾本教程涵盖的主要内容和学习重点。\n"
            f"2. 强调学习者通过本教程掌握的关键技能。\n"
            f"3. 鼓励学习者动手实践，并提供一些练习建议（如果可能）。\n"
            f"4. （可选）指出可以进一步学习的相关资源或项目的高级特性。\n"
            f"5. 感谢观看并引导观众进行互动（点赞、评论、订阅等）。\n"
            f"请加入视觉提示，例如：[显示教程重点回顾列表]、[显示项目GitHub链接或文档链接]、[显示结束卡片和社交媒体图标]。"
        )
    
    else: # 对于 core_features_parent 或其他未明确处理的类型
        print(f"  [!] 注意: 暂未为教程部分类型 '{section_type}' 定义特定的脚本生成逻辑。将尝试通用生成。")
        content_source = section_data.get("content_source", title) # Fallback to title or other available info
        script_prompt = (
            f"为视频教程中标题为 '{title}' 的部分生成脚本内容。\n"
            f"相关信息：{content_source}\n"
            f"请确保内容清晰、有条理，并加入适当的视觉提示，如 [显示相关图表] 或 [高亮关键信息]。"
        )


    if not script_prompt:
        print(f"  [!] 未能为教程部分 '{title}' 构建有效的提示。")
        return None

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": script_prompt}
    ]
    
    section_script = _make_llm_call_for_script(client, messages, MAX_TOKENS_SCRIPT_SECTION)
    
    if section_script:
        print(f"  <- 已收到教程部分 '{title}' 的脚本。")
    else:
        print(f"  <!> 未能为教程部分 '{title}' 生成脚本。")
    return section_script


def generate_full_tutorial_script(client: Any, tutorial_outline: List[Dict[str, Any]], project_name: str, target_audience: str = "初学者") -> List[Dict[str, Any]]:
    """
    遍历教程大纲，为每个部分生成脚本，并组装成完整的教程脚本。
    返回的列表每个元素包含该部分的标题、类型和生成的脚本。
    """
    full_script_parts = []
    print(f"\n开始为项目 '{project_name}' 生成完整教程脚本...")

    for section_data in tutorial_outline:
        if section_data["section_type"] == "core_features_parent":
            # 对于父部分，我们可以选择生成一个过渡性的介绍
            parent_title = section_data.get("title")
            # 或者直接处理其子部分
            print(f"\n  处理核心功能组: '{parent_title}'...")
            for sub_section_data in section_data.get("sub_sections", []):
                script_content = generate_script_for_section(client, sub_section_data, project_name, target_audience)
                full_script_parts.append({
                    "title": sub_section_data.get("title"),
                    "type": sub_section_data.get("section_type"),
                    "script": script_content if script_content else "# 未能生成此部分的脚本"
                })
                time.sleep(API_CALL_DELAY_SECONDS) # API调用间的延迟
        else:
            script_content = generate_script_for_section(client, section_data, project_name, target_audience)
            full_script_parts.append({
                "title": section_data.get("title"),
                "type": section_data.get("section_type"),
                "script": script_content if script_content else "# 未能生成此部分的脚本"
            })
            time.sleep(API_CALL_DELAY_SECONDS) # API调用间的延迟
            
    print(f"\n完整教程脚本已生成 {len(full_script_parts)} 个部分。")
    return full_script_parts

# --- 可选: 用于直接测试本模块的功能 ---
if __name__ == '__main__':
    print("--- 测试 Script Generator 模块 ---")
    # 需要一个 DeepSeek 客户端实例 和一个 教程大纲结构 来进行测试
    # 这里仅为演示，实际测试时你需要提供这些依赖

    # 示例: 模拟客户端 (实际应从 deepseek_client.py 初始化)
    class MockDeepSeekClient:
        def chat(self): return self
        def completions(self): return self
        def create(self, model, messages, max_tokens, temperature):
            print("\n--- MOCK API CALL ---")
            print(f"Model: {model}")
            # print(f"Messages: {messages}")
            print(f"Max Tokens: {max_tokens}, Temperature: {temperature}")
            # 取出用户消息的最后一部分作为模拟回复
            user_content = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "没有用户消息")
            return type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'message': type('obj', (object,), {'content': f"这是针对 '{user_content[:50]}...' 的模拟脚本回复。\n[视觉提示：显示一些很酷的东西！]"})
                })]
            })

    mock_client = MockDeepSeekClient()
    test_project_name_script = "我的示例项目"
    
    # 示例: 模拟教程大纲 (实际应从 tutorial_planner.py 生成)
    sample_outline = [
        {"section_type": "introduction", "title": "欢迎", "content_source": "一个测试项目", "project_name": test_project_name_script},
        {"section_type": "core_features_parent", "title": "核心功能", "sub_sections": [
            {"section_type": "core_feature_detail", "title": "功能A：做某事", "element_name": "do_something", "element_type": "function", "code_snippet": "def do_something():\n  pass", "explanation": "这个函数用来做某事。"},
        ]},
        {"section_type": "conclusion", "title": "总结", "content_source": "总结一下。"},
    ]

    generated_scripts = generate_full_tutorial_script(mock_client, sample_outline, test_project_name_script)

    if generated_scripts:
        print("\n--- 生成的完整教程脚本 (部分) ---")
        for i, part in enumerate(generated_scripts):
            print(f"\n--- 部分 {i+1}: {part['title']} ({part['type']}) ---")
            print(part['script'][:300] + "..." if part['script'] else "# 无脚本") # 打印脚本片段
            
        # 在实际应用中，你可能想将 generated_scripts 保存到文件
        # 例如，保存为一个大的文本文件或JSON文件
        output_script_file = "tutorial_script_output.txt"
        with open(output_script_file, "w", encoding="utf-8") as f:
            for part in generated_scripts:
                f.write(f"--- {part['title']} ({part['type']}) ---\n\n")
                f.write(f"{part['script']}\n\n=====================================\n\n")
        print(f"\n完整脚本已（模拟）保存到 {output_script_file}")