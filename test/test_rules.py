import pytest
from app.scan.scanner import _scan_single_file, run_bandit_scan

def test_pickle_detection(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("import pickle\npickle.loads(b'data')")
    result = _scan_single_file(temp_py_file)
    issues = result['results']
    assert len(issues) == 1
    assert 'pickle.loads' in issues[0]['issue_text']
    assert issues[0]['severity'] == 'HIGH'

def test_yaml_detection(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("import yaml\nyaml.load('doc')")
    result = _scan_single_file(temp_py_file)
    issues = result['results']
    assert len(issues) == 1
    assert 'yaml.load' in issues[0]['issue_text']
    assert issues[0]['severity'] == 'MEDIUM'

def test_eval_detection(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("eval('1+1')")
    result = _scan_single_file(temp_py_file)
    issues = result['results']
    assert len(issues) == 1
    assert issues[0]['test_name'] == 'detect_code_injection'
    assert issues[0]['severity'] == 'HIGH'

def test_os_system_detection(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("import os\nos.system('ls')")
    result = _scan_single_file(temp_py_file)
    issues = result['results']
    assert len(issues) == 1
    assert 'os.system' in issues[0]['issue_text']

def test_subprocess_detection(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("import subprocess\nsubprocess.run('ls', shell=True)")
    result = _scan_single_file(temp_py_file)
    issues = result['results']
    assert len(issues) == 1
    assert 'subprocess.run' in issues[0]['issue_text']

def test_directory_scan():
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, 'a.py'), 'w') as f:
            f.write("pickle.loads(b'x')")
        with open(os.path.join(tmpdir, 'b.py'), 'w') as f:
            f.write("eval('1')")
        result = run_bandit_scan(tmpdir)
        assert len(result['results']) == 2

def test_no_false_positive(temp_py_file):
    with open(temp_py_file, 'w') as f:
        f.write("import json\njson.loads('{}')")
    result = _scan_single_file(temp_py_file)
    assert len(result['results']) == 0