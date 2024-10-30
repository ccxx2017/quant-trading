import os
from typing import List

def print_structure(startpath: str, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', '.pytest_cache', '.venv', 'venv']
    if exclude_files is None:
        exclude_files = ['.gitignore', '.env', 'print_structure.py']
    
    output = []
    for root, dirs, files in os.walk(startpath):
        # 排除不需要的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        output.append(f'{indent}📁 {os.path.basename(root)}/')
        
        subindent = '│   ' * (level + 1)
        for f in sorted(files):
            if f not in exclude_files and not f.endswith('.pyc'):
                output.append(f'{subindent}📄 {f}')
    
    return '\n'.join(output)

if __name__ == '__main__':
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    structure = print_structure(current_dir)
    print(structure)
    
    # 同时保存到文件
    with open('project_structure.txt', 'w', encoding='utf-8') as f:
        f.write(structure)
