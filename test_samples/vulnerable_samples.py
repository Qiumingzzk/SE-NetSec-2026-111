import pickle
import yaml
import joblib
import numpy as np
import os
import subprocess

def unsafe_pickle(data):
    obj = pickle.loads(data)  # 高危

def unsafe_yaml(data):
    obj = yaml.load(data)     # 中危

def unsafe_joblib(path):
    model = joblib.load(path) # 中危

def unsafe_numpy(path):
    arr = np.load(path, allow_pickle=True)  # 中危

def unsafe_eval(code):
    eval(code)                # 高危

def unsafe_os():
    os.system('rm -rf /')     # 高危

def unsafe_subprocess():
    subprocess.run('ls', shell=True)  # 高危