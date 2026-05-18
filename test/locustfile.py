from locust import HttpUser, task, between
import json

class ScanUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # 注册并登录获取 token
        self.client.post("/auth/register",
                         json={"username": f"locust_{self.id}", "password": "test"})
        resp = self.client.post("/auth/login",
                                json={"username": f"locust_{self.id}", "password": "test"})
        self.token = resp.json()["access_token"]

    @task(3)
    def start_scan(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.post("/scan/start",
                              json={"target_path": "test_samples/vulnerable_samples.py"},
                              headers=headers,
                              catch_response=True) as resp:
            if resp.status_code == 202:
                task_id = resp.json()["task_id"]
                # 可选：轮询结果（为避免过度负载，不在此处轮询）
            else:
                resp.failure(f"Scan start failed: {resp.text}")

    @task(1)
    def history(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/scan/history?page=1&per_page=5", headers=headers)