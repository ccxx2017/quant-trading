import os

def collect_code(root_dir: str, output_file: str):
    """收集项目中的代码文件并写入单个文件"""
    
    # 要收集的文件扩展名
    CODE_EXTENSIONS = {'.py', '.html', '.css', '.js'}
    
    # 要排除的目录
    EXCLUDE_DIRS = {'__pycache__', '.git', 'venv', '.venv', 'logs'}
    
    # 要排除的文件
    EXCLUDE_FILES = {'__init__.py'}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(root_dir):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                # 检查文件扩展名
                if os.path.splitext(file)[1] in CODE_EXTENSIONS and file not in EXCLUDE_FILES:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as code_file:
                            content = code_file.read()
                            
                            # 写入分隔符和文件路径
                            f.write(f"\n{'='*80}\n")
                            f.write(f"File: {relative_path}\n")
                            f.write(f"{'='*80}\n\n")
                            
                            # 写入代码内容
                            f.write(content)
                            f.write("\n")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    # 获取当前目录的父目录（项目根目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "project_code.txt")
    
    collect_code(project_root, output_file)
    print(f"Code collection completed. Output saved to {output_file}")