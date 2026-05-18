import pytest
import tempfile
import os
from app import create_app
from app.extensions import db as _db
from app.models import User, ScanTask

@pytest.fixture(scope='session')
def app():
    """创建 Flask 应用实例（测试配置）"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 使用内存数据库
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    return app

@pytest.fixture(scope='session')
def db(app):
    """创建数据库表"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    """测试客户端"""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(client):
    """注册并登录，返回 JWT 认证头"""
    client.post('/auth/register', json={'username': 'testuser', 'password': 'testpass'})
    resp = client.post('/auth/login', json={'username': 'testuser', 'password': 'testpass'})
    token = resp.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def temp_py_file():
    """创建临时 Python 文件，用于扫描测试"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        yield f.name
    os.unlink(f.name)