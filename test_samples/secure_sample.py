import json
import yaml
import numpy as np

def safe_pickle(data):
    obj = json.loads(data)   # 安全

def safe_yaml(data):
    obj = yaml.safe_load(data)  # 安全

def safe_numpy(path):
    arr = np.load(path, allow_pickle=False)  # 安全