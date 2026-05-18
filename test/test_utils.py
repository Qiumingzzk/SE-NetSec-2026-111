import tempfile
import os
from app.scan.snippet import get_code_snippet
from app.scan.comparator import compare_scan_results
from app.scan.upload import process_zip_upload
from werkzeug.datastructures import FileStorage

def test_snippet():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("line1\nline2\nline3\nline4\nline5")
        f.flush()
        result = get_code_snippet(f.name, line_number=3, context_lines=1)
        assert 'snippet' in result
        assert 'line4' in result['snippet']  # 因为 context_lines=1，包含第3行周围
    os.unlink(f.name)

def test_compare():
    result1 = {"results": [{"filename":"a.py","line_number":1,"test_name":"t1"}]}
    result2 = {"results": [{"filename":"b.py","line_number":2,"test_name":"t2"}]}
    comp = compare_scan_results(result1, result2)
    assert len(comp['new']) == 1
    assert len(comp['fixed']) == 1
    assert len(comp['persistent']) == 0

def test_compare_empty():
    result1 = {"results": []}
    result2 = {"results": [{"filename":"b.py","line_number":2,"test_name":"t2"}]}
    comp = compare_scan_results(result1, result2)
    assert len(comp['new']) == 1
    assert len(comp['fixed']) == 0

def test_zip_upload():
    # 创建一个临时 ZIP 文件
    import zipfile
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as zip_file:
        with zipfile.ZipFile(zip_file.name, 'w') as zf:
            zf.writestr('test.py', 'print("hello")')
        zip_file.flush()
        # 模拟上传文件对象
        with open(zip_file.name, 'rb') as f:
            file_storage = FileStorage(f, filename='test.zip')
            extract_path = process_zip_upload(file_storage, extract_to='/tmp/test_uploads')
        assert os.path.exists(os.path.join(extract_path, 'test.py'))
        # 清理
        import shutil
        shutil.rmtree(extract_path)
    os.unlink(zip_file.name)