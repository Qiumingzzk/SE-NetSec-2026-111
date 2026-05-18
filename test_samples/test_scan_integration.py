import pytest
import time
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_scan_single_file(client):
    # 注册用户
    client.post('/auth/register', json={'username':'test','password':'pass'})
    login = client.post('/auth/login', json={'username':'test','password':'pass'})
    token = login.json['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 发起扫描
    resp = client.post('/scan/start', headers=headers, json={'target_path':'test_samples/vulnerable_samples.py'})
    assert resp.status_code == 202
    task_id = resp.json['task_id']

    # 轮询结果
    for _ in range(10):
        res = client.get(f'/scan/result/{task_id}', headers=headers)
        if res.json['status'] == 'completed':
            break
        time.sleep(1)
    assert len(res.json['result']['results']) >= 3

def test_scan_directory(client):
    client.post('/auth/register', json={'username':'test2','password':'pass'})
    login = client.post('/auth/login', json={'username':'test2','password':'pass'})
    token = login.json['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post('/scan/start', headers=headers, json={'target_path':'test_samples/'})
    assert resp.status_code == 202
    task_id = resp.json['task_id']
    for _ in range(10):
        res = client.get(f'/scan/result/{task_id}', headers=headers)
        if res.json['status'] == 'completed':
            break
        time.sleep(1)
    # 目录扫描应至少包含两个文件的漏洞
    assert len(res.json['result']['results']) >= 3