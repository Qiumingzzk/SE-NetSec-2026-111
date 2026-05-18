# secure_extra3.py（修复版）
import pickle
import yaml
import json

# 修复1：使用安全反序列化替代 pickle.loads
# 原：obj = pickle.loads(b"malicious")
# 修复：使用 JSON 或仅处理可信数据（此处改为 json.loads）
data = b'{"key": "value"}'
obj = json.loads(data.decode())   # 安全

# 修复2：使用 yaml.safe_load 替代 yaml.load
doc = "name: John"
obj_yaml = yaml.safe_load(doc)    # 安全

# 修复3：移除 eval，改用安全计算或直接赋值
user_input = "2+2"
# 原：eval(user_input)  -> 危险
# 修复：使用 ast.literal_eval 进行安全计算，或直接处理已知逻辑
import ast
result = ast.literal_eval(user_input) if user_input.isnumeric() else 0

# 额外：移除任何命令注入风险，不引入 os.system 等调用