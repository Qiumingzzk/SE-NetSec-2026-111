import base64
import hashlib

# 硬编码 API 密钥
API_KEY = "sk-1234567890abcdef"
SECRET_TOKEN = "my_secret_token_123"

# 弱哈希算法（MD5）
password = "admin123"
hash_md5 = hashlib.md5(password.encode()).hexdigest()

# base64 伪隐藏（等于明文）
encoded = base64.b64encode(b"real_password").decode()