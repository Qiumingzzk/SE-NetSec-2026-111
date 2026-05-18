import time

def test_register(client):
    resp = client.post('/auth/register', json={'username': 'newuser', 'password': 'pass'})
    assert resp.status_code == 201
    assert resp.json['msg'] == 'Registered successfully'

def test_register_duplicate(client):
    client.post('/auth/register', json={'username': 'dup', 'password': 'pass'})
    resp = client.post('/auth/register', json={'username': 'dup', 'password': 'pass'})
    assert resp.status_code == 400
    assert 'User already exists' in resp.json['msg']

def test_login(client):
    client.post('/auth/register', json={'username': 'loginuser', 'password': 'pass'})
    resp = client.post('/auth/login', json={'username': 'loginuser', 'password': 'pass'})
    assert resp.status_code == 200
    assert 'access_token' in resp.json

def test_start_scan(client, auth_headers):
    resp = client.post('/scan/start',
                       json={'target_path': 'test_samples/vulnerable_samples.py'},
                       headers=auth_headers)
    assert resp.status_code == 202
    assert 'task_id' in resp.json

def test_get_result(client, auth_headers):
    # 先启动扫描
    start = client.post('/scan/start',
                        json={'target_path': 'test_samples/vulnerable_samples.py'},
                        headers=auth_headers)
    task_id = start.json['task_id']
    # 轮询结果（最多等待 30 秒）
    for _ in range(15):
        time.sleep(2)
        resp = client.get(f'/scan/result/{task_id}', headers=auth_headers)
        if resp.json['status'] == 'completed':
            break
    assert resp.json['status'] == 'completed'
    assert 'results' in resp.json['result']

def test_history(client, auth_headers):
    resp = client.get('/scan/history?page=1&per_page=5', headers=auth_headers)
    assert resp.status_code == 200
    assert 'tasks' in resp.json
    assert 'total' in resp.json

def test_export_csv(client, auth_headers):
    # 需要有一个已完成的扫描任务
    start = client.post('/scan/start',
                        json={'target_path': 'test_samples/vulnerable_samples.py'},
                        headers=auth_headers)
    task_id = start.json['task_id']
    for _ in range(15):
        time.sleep(2)
        status_resp = client.get(f'/scan/result/{task_id}', headers=auth_headers)
        if status_resp.json['status'] == 'completed':
            break
    export_resp = client.get(f'/scan/export/{task_id}', headers=auth_headers)
    assert export_resp.status_code == 200
    assert 'text/csv' in export_resp.content_type

def test_compare(client, auth_headers):
    # 创建两个已完成的扫描任务（简化：先扫描同一个文件两次，得到两个 ID）
    start1 = client.post('/scan/start', json={'target_path': 'test_samples/vulnerable_samples.py'}, headers=auth_headers)
    id1 = start1.json['task_id']
    start2 = client.post('/scan/start', json={'target_path': 'test_samples/vulnerable_samples.py'}, headers=auth_headers)
    id2 = start2.json['task_id']
    # 等待完成
    for _ in range(15):
        time.sleep(2)
        r1 = client.get(f'/scan/result/{id1}', headers=auth_headers)
        r2 = client.get(f'/scan/result/{id2}', headers=auth_headers)
        if r1.json['status'] == 'completed' and r2.json['status'] == 'completed':
            break
    compare_resp = client.get(f'/scan/compare/{id1}/{id2}', headers=auth_headers)
    assert compare_resp.status_code == 200
    assert 'new' in compare_resp.json
    assert 'fixed' in compare_resp.json
    assert 'persistent' in compare_resp.json