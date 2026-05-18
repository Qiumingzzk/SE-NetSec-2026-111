import json
import yaml
import os

# 安全部分
safe_data = json.loads('{"a":1}')
yaml_safe = yaml.safe_load("name: John")

# 不安全部分
os.system("calc.exe")
eval("print('danger')")