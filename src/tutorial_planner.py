# src/tutorial_planner.py
import os
import json
from typing import List, Dict, Any, Optional # 保持类型提示的好习惯

def load_documentation_data(output_base_dir: str, project_name: str) -> List[Dict[str, Any]]:
    """
    从指定的JSON文件加载文档化元素数据。

    Args:
        output_base_dir (str): 存放生成的JSON文件的基础目录 (例如 "output_generated_docs")。
        project_name (str): 项目名称，用于构造JSON文件名。

    Returns:
        List[Dict[str, Any]]: 加载的文档化元素列表，如果失败则为空列表。
    """
    json_input_filename = f"{project_name}_documentation_data.json"
    # 注意：这里的 output_base_dir 是相对于当前工作目录的，
    # 如果 tutorial_planner.py 被 main.py 调用，那么 os.getcwd() 通常是项目根目录。
    json_input_path = os.path.join(output_base_dir, json_input_filename)

    loaded_elements: List[Dict[str, Any]] = []
    if os.path.exists(json_input_path):
        try:
            with open(json_input_path, 'r', encoding='utf-8') as f:
                loaded_elements = json.load(f)
            print(f"[Tutorial Planner] 成功从 {json_input_path} 加载了 {len(loaded_elements)} 个文档化元素。")
        except Exception as e:
            print(f"[Tutorial Planner] 从 {json_input_path} 加载数据失败: {e}")
    else:
        print(f"[Tutorial Planner] 未找到已保存的 JSON 数据文件: {json_input_path}。")
    
    return loaded_elements

def build_tutorial_outline(documented_elements: List[Dict[str, Any]], 
                           project_name: str, 
                           readme_overview: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    根据文档化元素和项目信息构建教程大纲。

    Args:
        documented_elements (List[Dict[str, Any]]): 从JSON加载的文档化元素列表。
        project_name (str): 项目名称。
        readme_overview (Optional[str]): 从步骤三生成的项目概览文本。

    Returns:
        List[Dict[str, Any]]: 表示教程大纲的列表。
    """
    if not documented_elements:
        print("[Tutorial Planner] 没有可用于构建教程大纲的文档化元素。")
        return []

    tutorial_outline: List[Dict[str, Any]] = []

    # A. 引言
    tutorial_outline.append({
        "section_type": "introduction",
        "title": f"欢迎学习 {project_name} 教程",
        "content_source": readme_overview if readme_overview else f"请基于 {project_name} 项目的目的和主要功能生成引言。",
        "project_name": project_name
    })

    # B. 环境设置
    tutorial_outline.append({
        "section_type": "setup",
        "title": "环境设置与安装",
        "content_source": f"请提供关于如何安装和配置 {project_name} 项目的说明。"
    })

    # C. 核心功能讲解
    core_features_section = {
        "section_type": "core_features_parent",
        "title": "核心功能详解",
        "sub_sections": []
    }

    elements_to_explain = sorted(
        [el for el in documented_elements if el.get('explanation') and el['type'] in ['function', 'method', 'class', 'async function', 'async method']],
        key=lambda x: (
            x.get('file_path', ''),        # 使用 .get 提供默认值以增加稳健性
            x.get('class_name') or '',     # 如果 class_name 是 None，则使用空字符串 '' 进行排序
            x.get('start_line', 0)         # 使用 .get 提供默认值
        )
    )

    for element in elements_to_explain:
        feature_title = f"{element['type'].capitalize()}：`{element['name']}`"
        if element.get('class_name'):
            feature_title = f"{element['type'].capitalize()}：`{element['class_name']}.{element['name']}`"
        
        core_features_section["sub_sections"].append({
            "section_type": "core_feature_detail",
            "title": feature_title,
            "element_name": element['name'],
            "element_type": element['type'],
            "element_class_name": element.get('class_name'),
            "code_snippet": element['code'],
            "explanation": element['explanation'],
            "file_path": element['file_path']
        })
    
    if core_features_section["sub_sections"]:
        tutorial_outline.append(core_features_section)

    # E. 总结与后续
    tutorial_outline.append({
        "section_type": "conclusion",
        "title": "总结与展望",
        "content_source": f"请对 {project_name} 教程内容进行总结，并提供学习建议或下一步指引。"
    })
    
    print(f"[Tutorial Planner] 教程大纲初步构建完成，包含 {len(tutorial_outline)} 个主要部分。")
    return tutorial_outline

# --- 可选: 用于直接测试本模块的功能 ---
if __name__ == '__main__':
    print("--- 测试 Tutorial Planner 模块 ---")
    # 假设 output_generated_docs 文件夹在当前工作目录的上一级（如果从 src 运行）
    # 或者直接相对于当前工作目录（如果从项目根目录运行 python -m src.tutorial_planner）
    
    # 为了能独立测试，我们需要知道项目根目录下的 output_generated_docs
    # 假设我们从项目根目录运行 python -m src.tutorial_planner
    current_working_dir = os.getcwd() # 通常是项目根目录
    test_output_base_dir = os.path.join(current_working_dir, "output_generated_docs")
    test_project_name = "src" # 你需要替换为实际的项目名，或者让用户输入

    # 尝试加载之前步骤生成的 README_overview.md (可选)
    test_readme_overview_content = None
    readme_path = os.path.join(test_output_base_dir, "README_overview.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                # 跳过可能的标题行
                lines = f.readlines()
                if lines and lines[0].startswith("#"):
                    test_readme_overview_content = "".join(lines[1:]).strip()
                else:
                    test_readme_overview_content = "".join(lines).strip()
            print(f"成功从 {readme_path} 加载了 README 概览。")
        except Exception as e:
            print(f"加载 README 概览失败: {e}")


    # 确保 JSON 文件存在才能测试
    # 你可能需要手动创建一个名为 "TestProject_documentation_data.json" 的示例文件在 output_generated_docs 中
    # 或者确保你的项目已经运行过步骤1-3并生成了此文件
    print(f"尝试从 {test_output_base_dir} 加载项目 '{test_project_name}' 的数据...")
    data = load_documentation_data(test_output_base_dir, test_project_name)

    if data:
        outline = build_tutorial_outline(data, test_project_name, test_readme_overview_content)
        if outline:
            print("\n--- 生成的教程大纲示例 ---")
            for section_idx, section in enumerate(outline):
                print(f"部分 {section_idx + 1}: {section['title']} (类型: {section['section_type']})")
                if section['section_type'] == 'core_features_parent':
                    print(f"  包含 {len(section['sub_sections'])} 个核心功能点:")
                    for sub_idx, sub_section in enumerate(section['sub_sections'][:2]): # 只打印前2个子部分
                        print(f"    {sub_idx + 1}. {sub_section['title']}")
    else:
        print("未能加载数据，无法构建大纲进行测试。")
        print(f"请确保 '{os.path.join(test_output_base_dir, test_project_name + '_documentation_data.json')}' 文件存在。")