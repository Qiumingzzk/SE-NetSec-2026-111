import zipfile
import os
import tempfile
import shutil

def process_zip_upload(zip_file, extract_to='/app/uploads'):
    os.makedirs(extract_to, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, 'upload.zip')
        zip_file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 安全防护：防止路径遍历
            for member in zf.namelist():
                member_path = os.path.join(extract_to, member)
                if not os.path.realpath(member_path).startswith(os.path.realpath(extract_to)):
                    raise ValueError("Zip file contains path traversal")
            zf.extractall(extract_to)
    return extract_to