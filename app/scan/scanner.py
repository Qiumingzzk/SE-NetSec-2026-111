import os
import ast
import json
from functools import lru_cache

def run_bandit_scan(target_path: str, cancel_check=None):
    if not os.path.exists(target_path):
        return {"error": f"Path does not exist: {target_path}"}
    if os.path.isfile(target_path):
        return _scan_single_file(target_path, cancel_check)
    else:
        return _scan_directory(target_path, cancel_check)

@lru_cache(maxsize=128)
def _scan_single_file_cached(file_path: str, cancel_check=None):
    # 注意：lru_cache 不能处理可变参数 cancel_check，实际调用时忽略取消检查或单独处理
    return _scan_single_file(file_path, cancel_check)

def _scan_single_file(file_path: str, cancel_check=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
        return {"error": f"Failed to parse file: {e}", "results": []}

    issues = []
    for node in ast.walk(tree):
        if cancel_check and cancel_check():
            return {"results": [], "error": "cancelled"}
        if isinstance(node, ast.Call):
            func = node.func
            # 获取完整函数名
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    full_name = f"{func.value.id}.{func.attr}"
                else:
                    full_name = func.attr
            elif isinstance(func, ast.Name):
                full_name = func.id
            else:
                continue

            # ----- 危险函数检测列表 -----
            # 1. 不安全反序列化
            if full_name in ('pickle.load', 'pickle.loads'):
                issues.append(create_issue(file_path, node.lineno, "HIGH", "pickle", full_name))
            elif full_name == 'yaml.load':
                issues.append(create_issue(file_path, node.lineno, "MEDIUM", "yaml", full_name))
            elif full_name == 'joblib.load':
                issues.append(create_issue(file_path, node.lineno, "MEDIUM", "joblib", full_name))
            elif full_name == 'numpy.load':
                allow_pickle = False
                for kw in node.keywords:
                    if kw.arg == 'allow_pickle' and isinstance(kw.value, ast.Constant):
                        allow_pickle = kw.value.value
                if allow_pickle:
                    issues.append(create_issue(file_path, node.lineno, "MEDIUM", "numpy", full_name))
            # 2. 动态代码执行
            elif full_name in ('eval', 'exec'):
                issues.append(create_issue(file_path, node.lineno, "HIGH", "eval_exec", full_name))
            # 3. 系统命令执行
            elif full_name in ('os.system', 'os.popen', 'os.popen2', 'os.popen3'):
                issues.append(create_issue(file_path, node.lineno, "HIGH", "os_system", full_name))
            elif full_name in ('subprocess.run', 'subprocess.call', 'subprocess.Popen', 'subprocess.check_output'):
                issues.append(create_issue(file_path, node.lineno, "HIGH", "subprocess", full_name))
    return format_output(issues)

def _scan_directory(dir_path: str, cancel_check=None):
    all_issues = []
    for root, dirs, files in os.walk(dir_path):
        if cancel_check and cancel_check():
            return {"results": [], "error": "cancelled"}
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'venv', '.git', 'migrations', 'node_modules')]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # 使用缓存版本，注意取消检查传入（缓存会忽略 cancel_check，但目录扫描中可接受）
                result = _scan_single_file_cached(full_path, cancel_check)
                if result and 'results' in result:
                    for issue in result['results']:
                        issue['filename'] = full_path  # 确保绝对路径
                    all_issues.extend(result['results'])
    return format_output(all_issues)

def create_issue(file_path, line, severity, rule_type, func_name):
    """生成标准 issue 字典"""
    if rule_type == 'pickle':
        text = f"Insecure deserialization: {func_name} may lead to RCE. Do not load untrusted data."
        cwe = 502
    elif rule_type == 'yaml':
        text = "yaml.load with default loader is unsafe. Use yaml.safe_load instead."
        cwe = 502
    elif rule_type == 'joblib':
        text = "joblib.load is based on pickle, unsafe for untrusted data."
        cwe = 502
    elif rule_type == 'numpy':
        text = "numpy.load with allow_pickle=True may allow arbitrary code execution."
        cwe = 502
    elif rule_type == 'eval_exec':
        text = f"Dynamic code execution using {func_name} can lead to arbitrary code execution if input is untrusted."
        cwe = 94
    elif rule_type == 'os_system':
        text = f"System command execution using {func_name} can lead to command injection if input is untrusted."
        cwe = 78
    elif rule_type == 'subprocess':
        text = f"Subprocess execution using {func_name} may be dangerous if shell=True or input is untrusted."
        cwe = 78
    else:
        text = f"Potential security issue: {func_name}"
        cwe = 0
    return {
        "test_name": "detect_insecure_deserialization" if cwe==502 else "detect_code_injection",
        "test_id": "B999" if cwe==502 else "B700",
        "severity": severity,
        "confidence": "HIGH",
        "line_number": line,
        "line_range": [line],
        "filename": file_path,
        "issue_text": text,
        "issue_cwe": {"id": cwe},
        "issue_severity": severity
    }

def format_output(issues):
    output = {
        "results": issues,
        "errors": [],
        "metrics": {
            "totals": {
                "SEVERITY": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "CONFIDENCE": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            }
        }
    }
    for issue in issues:
        sev = issue["severity"]
        output["metrics"]["totals"]["SEVERITY"][sev] = output["metrics"]["totals"]["SEVERITY"].get(sev, 0) + 1
        conf = issue["confidence"]
        output["metrics"]["totals"]["CONFIDENCE"][conf] = output["metrics"]["totals"]["CONFIDENCE"].get(conf, 0) + 1
    return output