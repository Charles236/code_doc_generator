# src/main.py
import os
import json # <--- 确保导入 json 模块

# 步骤一: 从 deepseek_client.py 导入
from .deepseek_client import initialize_deepseek_client #

# 步骤二: 从 code_parser.py 导入
from .code_parser import get_codebase_path_from_user, find_python_files, extract_code_elements_from_file #

# 步骤三: 从 doc_generator.py 导入
from .doc_generator import process_elements_for_docs, generate_project_overview #


def sanitize_filename(name_part: str) -> str:
    """
    清理字符串，使其适合作为文件名的一部分。
    移除或替换不安全/不合适的字符。
    """
    if not name_part:
        return ""
    name_part = str(name_part) # 确保是字符串
    # 替换路径分隔符，移除不期望的字符
    name_part = name_part.replace(os.path.sep, '_')
    # 只保留字母数字、空格、点、下划线、中横线
    valid_chars = "".join(c for c in name_part if c.isalnum() or c in (' ', '.', '_', '-')).strip()
    # 避免文件名过长，并替换空格为下划线
    return valid_chars[:60].replace(' ', '_')


if __name__ == "__main__":
    print("--- 自动化代码文档和教程生成器 ---")

    # --- 步骤 1: DeepSeek 客户端初始化 ---
    print("\n--- 步骤 1: DeepSeek 客户端初始化 ---")
    deepseek_client = initialize_deepseek_client() #

    if not deepseek_client:
        print("DeepSeek 客户端初始化失败。正在退出。") #
        exit()
    else:
        print("DeepSeek 客户端已成功初始化。") #


    # --- 步骤 2: 输入代码处理 ---
    print("\n--- 步骤 2: 输入代码处理 ---") #
    codebase_path = get_codebase_path_from_user() #
    project_name = os.path.basename(codebase_path) if codebase_path else "Unknown_Project" #


    all_extracted_code_elements = []
    if codebase_path: #
        python_files = find_python_files(codebase_path) #
        if python_files: #
            print(f"\n共找到 {len(python_files)} 个 Python 文件。开始提取代码元素...") #
            for py_file in python_files: #
                elements = extract_code_elements_from_file(py_file) #
                all_extracted_code_elements.extend(elements) #
            
            print(f"\n--- 代码元素提取完成 ---") #
            print(f"总共提取了 {len(all_extracted_code_elements)} 个代码元素。") #
        else:
            print("在指定路径下未找到 Python 文件，无法继续。") #
    else:
        print("未提供有效的代码库路径，无法继续。") #

    print("\n--- 步骤 2 完成 ---") #

    # 定义输出目录的基础路径 (例如：在项目根目录下创建一个 'output' 文件夹)
    # os.getcwd() 通常是项目根目录（当你从根目录运行 python -m src.main 时）
    output_base_dir = os.path.join(os.getcwd(), "output_generated_docs") 
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir) # 创建 output_generated_docs 文件夹


    # --- 步骤 3: 生成代码解释和文档字符串 ---
    documented_elements = []
    readme_overview = None # 初始化 readme_overview
    if deepseek_client and all_extracted_code_elements: #
        print("\n--- 步骤 3: 生成代码解释和文档字符串 ---") #
        documented_elements = process_elements_for_docs(deepseek_client, all_extracted_code_elements) #
        
        print("\n--- 文档生成完成 ---") #
        generated_count = sum(1 for el in documented_elements if el.get('explanation') or el.get('docstring')) #
        print(f"为 {generated_count} 个元素生成了文档内容。") #

        # 打印一些示例 (这部分保持不变)
        print("\n示例文档内容 (最多前 2 个元素):") #
        for i, element in enumerate(documented_elements[:2]): #
            if element.get('explanation') or element.get('docstring'): #
                print(f"\n  元素: {element['type']} '{element['name']}' (来自 {os.path.basename(element['file_path'])})") #
                if element.get('explanation'): #
                    print(f"    说明: {element['explanation'][:200]}...") #
                if element.get('docstring'): #
                    docstring_preview = element['docstring'].replace('\n', '\n      ') #
                    print(f"    文档字符串:\n      \"\"\"\n      {docstring_preview}\n      \"\"\"") #
                print("-" * 30) #
        
        # (可选) 生成 README 项目概览
        print("\n--- (可选) 生成 README 项目概览 ---") #
        readme_overview = generate_project_overview(deepseek_client, documented_elements, project_name) #
        if readme_overview: #
            print("\n生成的项目概览:") #
            print("=" * 50) #
            print(readme_overview) #
            print("=" * 50) #
        else:
            print("未能生成项目概览。") #

        # --- VVVV 文件保存逻辑开始 VVVV ---

        # 1. 将 documented_elements 完整保存为 JSON 文件
        if documented_elements:
            json_output_filename = f"{project_name}_documentation_data.json"
            json_output_path = os.path.join(output_base_dir, json_output_filename)
            try:
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(documented_elements, f, ensure_ascii=False, indent=4)
                print(f"\n✅ [JSON] 所有文档数据已成功保存到: {json_output_path}")
            except Exception as e:
                print(f"\n❌ [JSON] 保存所有文档数据到 JSON 文件时出错: {e}")

        # 2. 单独保存每个解释和文档字符串到文本文件，以及README概览
        if documented_elements:
            output_individual_parent_dir = os.path.join(output_base_dir, "individual_files")
            if not os.path.exists(output_individual_parent_dir):
                os.makedirs(output_individual_parent_dir)

            print(f"\n正在单独保存每个文档和解释到文本文件: {output_individual_parent_dir}")

            for idx, element in enumerate(documented_elements):
                try:
                    relative_file_path = os.path.relpath(element['file_path'], codebase_path if codebase_path else os.getcwd())
                except ValueError: 
                    relative_file_path = os.path.basename(element['file_path'])

                path_part = sanitize_filename(os.path.splitext(relative_file_path)[0])
                class_part = sanitize_filename(element.get('class_name'))
                name_part = sanitize_filename(element['name'])
                
                filename_parts = [part for part in [path_part, class_part, name_part] if part]
                base_filename = "_".join(filename_parts)
                if not base_filename:
                    base_filename = f"element_{idx}"

                # 保存解释
                if element.get('explanation'):
                    explanation_filename = f"{base_filename}_explanation.txt"
                    explanation_filepath = os.path.join(output_individual_parent_dir, explanation_filename)
                    try:
                        with open(explanation_filepath, 'w', encoding='utf-8') as f:
                            f.write(f"File: {element['file_path']}\n")
                            f.write(f"Type: {element['type']}\n")
                            f.write(f"Name: {element['name']}\n")
                            if element.get('class_name'):
                                f.write(f"Class: {element['class_name']}\n")
                            f.write("-" * 30 + "\n\n")
                            f.write(element['explanation'])
                    except Exception as e:
                        print(f"  [!] 保存解释到 '{explanation_filepath}' 时出错: {e}")

                # 保存文档字符串
                if element.get('docstring'):
                    docstring_filename = f"{base_filename}_docstring.txt"
                    docstring_filepath = os.path.join(output_individual_parent_dir, docstring_filename)
                    try:
                        with open(docstring_filepath, 'w', encoding='utf-8') as f:
                            f.write(f"File: {element['file_path']}\n")
                            f.write(f"Type: {element['type']}\n")
                            f.write(f"Name: {element['name']}\n")
                            if element.get('class_name'):
                                f.write(f"Class: {element['class_name']}\n")
                            f.write("-" * 30 + "\n\n")
                            f.write(f'"""\n{element["docstring"]}\n"""')
                    except Exception as e:
                        print(f"  [!] 保存文档字符串到 '{docstring_filepath}' 时出错: {e}")
            print(f"\n✅ [TXT] 单独文件保存完成。")
        
        # 3. 保存 README 概览到 .md 文件
        if readme_overview:
            readme_filename = "README_overview.md"
            readme_filepath = os.path.join(output_base_dir, readme_filename) # 直接保存在 output_base_dir
            try:
                with open(readme_filepath, 'w', encoding='utf-8') as f:
                    f.write(readme_overview)
                print(f"\n✅ [MD] README 概览已成功保存到: {readme_filepath}")
            except Exception as e:
                print(f"\n❌ [MD] 保存 README 概览时出错: {e}")
        
        # --- ^^^^ 文件保存逻辑结束 ^^^^ ---

    elif not deepseek_client: #
        print("\n跳过步骤 3，因为 DeepSeek 客户端未成功初始化。") #
    elif not all_extracted_code_elements: #
        print("\n跳过步骤 3，因为步骤 2 未提取到任何代码元素。") #
    
    print("\n--- 步骤 3 完成 ---") #

    print("\n--- 所有基础步骤处理完毕 ---") #