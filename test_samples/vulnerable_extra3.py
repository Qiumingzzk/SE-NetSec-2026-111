import pickle
import yaml

data = b"malicious"
obj = pickle.loads(data)          # 反序列化

doc = "!!python/object/apply:os.system ['ls']"
yaml.load(doc)                    # 不安全 yaml

# 动态表达式注入
user_input = "__import__('os').system('whoami')"
eval(user_input)