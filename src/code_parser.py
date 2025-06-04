# src/code_parser.py

import os
import ast # Python's Abstract Syntax Tree module

def get_codebase_path_from_user() -> str | None:
    """
    Prompts the user to enter the path to their codebase directory.
    Validates if the path exists and is a directory.

    Returns:
        str: The validated absolute path to the codebase directory, or None if invalid.
    """
    while True:
        codebase_path = input("请输入您的代码库的本地目录路径 (例如 D:\\projects\\my_python_project): ").strip()
        if not codebase_path:
            print("路径不能为空，请重新输入。")
            continue

        # Convert to absolute path and normalize
        absolute_path = os.path.abspath(codebase_path)

        if not os.path.exists(absolute_path):
            print(f"错误：路径 '{absolute_path}' 不存在。请检查路径是否正确。")
        elif not os.path.isdir(absolute_path):
            print(f"错误：路径 '{absolute_path}' 不是一个有效的目录。")
        else:
            print(f"代码库路径确认为: {absolute_path}")
            return absolute_path
        
        try_again = input("要尝试其他路径吗？(y/n): ").lower()
        if try_again != 'y':
            return None

def find_python_files(codebase_path: str) -> list[str]:
    """
    Traverses the codebase directory and finds all Python files (.py).

    Args:
        codebase_path (str): The root directory of the codebase.

    Returns:
        list[str]: A list of absolute paths to Python files found.
    """
    python_files = []
    print(f"\n正在扫描 '{codebase_path}' 中的 Python 文件...")
    for root, _, files in os.walk(codebase_path):
        # Skip venv directories
        if "venv" in root.split(os.sep) or ".venv" in root.split(os.sep):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
                print(f"  找到: {file_path}")
    if not python_files:
        print("未找到任何 Python (.py) 文件。")
    return python_files

def extract_code_elements_from_file(file_path: str) -> list[dict]:
    """
    Parses a single Python file and extracts functions, classes, and methods.
    Requires Python 3.8+ for ast.get_source_segment for accurate code extraction.

    Args:
        file_path (str): The absolute path to the Python file.

    Returns:
        list[dict]: A list of dictionaries, each representing a code element.
                    Each dictionary contains: 'file_path', 'name', 'type', 
                                           'code', 'start_line', 'end_line', 'class_name'.
    """
    print(f"  正在解析文件: {file_path}")
    extracted_elements = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code_full = f.read()
    except Exception as e:
        print(f"  [!] 读取文件错误 {file_path}: {e}")
        return extracted_elements

    try:
        tree = ast.parse(source_code_full, filename=file_path)
    except SyntaxError as e:
        print(f"  [!] 文件 {file_path} 中存在语法错误: {e}")
        return extracted_elements

    for node in tree.body: # Iterate over top-level nodes in the module
        current_class_name = None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Top-level function
            try:
                element_code = ast.get_source_segment(source_code_full, node)
                if element_code:
                    extracted_elements.append({
                        "file_path": file_path,
                        "name": node.name,
                        "type": "async function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                        "code": element_code,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "class_name": None
                    })
            except Exception as e:
                print(f"  [!] 提取函数 '{node.name}' 代码时出错: {e}")

        elif isinstance(node, ast.ClassDef):
            current_class_name = node.name
            try:
                class_code_segment = ast.get_source_segment(source_code_full, node)
                if class_code_segment:
                     extracted_elements.append({
                        "file_path": file_path,
                        "name": node.name,
                        "type": "class",
                        "code": class_code_segment, # Contains the full class code including methods
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "class_name": None
                    })
            except Exception as e:
                print(f"  [!] 提取类 '{node.name}' 定义代码时出错: {e}")

            for method_node in node.body:
                if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    try:
                        method_code = ast.get_source_segment(source_code_full, method_node)
                        if method_code:
                            extracted_elements.append({
                                "file_path": file_path,
                                "name": method_node.name,
                                "type": "async method" if isinstance(method_node, ast.AsyncFunctionDef) else "method",
                                "code": method_code,
                                "start_line": method_node.lineno,
                                "end_line": method_node.end_lineno,
                                "class_name": current_class_name
                            })
                    except Exception as e:
                        print(f"  [!] 提取方法 '{method_node.name}' (类 {current_class_name}) 代码时出错: {e}")
    
    if extracted_elements:
        print(f"  从 {os.path.basename(file_path)} 提取了 {len(extracted_elements)} 个元素。")
    return extracted_elements

# --- Optional: For testing this module directly ---
if __name__ == '__main__':
    print("--- 正在测试 code_parser.py 模块 ---")
    
    # 获取用户输入的路径
    test_codebase_path = get_codebase_path_from_user()

    all_test_elements = []
    if test_codebase_path:
        test_python_files = find_python_files(test_codebase_path)
        if test_python_files:
            print(f"\n共找到 {len(test_python_files)} 个 Python 文件进行测试。开始提取代码元素...")
            for test_py_file in test_python_files:
                elements = extract_code_elements_from_file(test_py_file)
                all_test_elements.extend(elements)
            
            print(f"\n--- 测试代码元素提取完成 ---")
            print(f"总共提取了 {len(all_test_elements)} 个代码元素 (函数、类、方法)。")

            if all_test_elements:
                print("\n提取元素示例 (最多前 5 个):")
                for i, element in enumerate(all_test_elements[:5]):
                    print(f"  元素 {i+1}:")
                    print(f"    文件: {element['file_path']}")
                    print(f"    名称: {element['name']}")
                    print(f"    类型: {element['type']}")
                    if element['class_name']:
                        print(f"    所属类: {element['class_name']}")
                    print(f"    行号: {element['start_line']}-{element['end_line']}")
                    # print(f"    代码片段: \n{element['code'][:100].strip()}...")
                    print("-" * 20)
        else:
            print("在指定路径下未找到 Python 文件，无法进行测试。")
    else:
        print("未提供有效的代码库路径，无法进行测试。")

    print("\n--- code_parser.py 模块测试结束 ---")