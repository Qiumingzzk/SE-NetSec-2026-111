import pytest
import tempfile
import os
from app.scan.scanner import _scan_single_file, run_bandit_scan

def test_pickle_detection():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import pickle\npickle.loads(b'data')")
        f.flush()
        result = _scan_single_file(f.name)
    issues = result['results']
    assert len(issues) == 1
    assert 'pickle.loads' in issues[0]['issue_text']
    assert issues[0]['severity'] == 'HIGH'

def test_eval_detection():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("eval('print(1)')")
        f.flush()
        result = _scan_single_file(f.name)
    issues = result['results']
    assert len(issues) == 1
    assert issues[0]['test_name'] == 'detect_code_injection'

def test_os_system_detection():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\nos.system('ls')")
        f.flush()
        result = _scan_single_file(f.name)
    issues = result['results']
    assert any('os.system' in i['issue_text'] for i in issues)

def test_directory_scan():
    test_dir = tempfile.mkdtemp()
    with open(os.path.join(test_dir, 'a.py'), 'w') as f:
        f.write("pickle.loads(b'x')")
    with open(os.path.join(test_dir, 'b.py'), 'w') as f:
        f.write("eval('1+1')")
    result = run_bandit_scan(test_dir)
    assert len(result['results']) == 2
    import shutil
    shutil.rmtree(test_dir)

def test_compare():
    from app.scan.comparator import compare_scan_results
    result1 = {"results": [{"filename":"a.py","line_number":1,"test_name":"t1"}]}
    result2 = {"results": [{"filename":"b.py","line_number":2,"test_name":"t2"}]}
    comp = compare_scan_results(result1, result2)
    assert len(comp['new']) == 1
    assert len(comp['fixed']) == 1
    assert len(comp['persistent']) == 0