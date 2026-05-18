import threading
import shutil
from datetime import datetime
from app.models import ScanTask, db
from .scanner import run_bandit_scan
from .sse import send_progress


def start_async_scan(task_id: int, target_path: str):
    def _run():
        from app import create_app
        app = create_app()
        with app.app_context():
            task = ScanTask.query.get(task_id)
            if not task:
                return
            try:
                # 发送开始进度
                send_progress(task_id, 10, "开始扫描...")
                task.status = 'running'
                db.session.commit()

                def is_cancelled():
                    t = ScanTask.query.get(task_id)
                    return t and t.cancel_requested

                # 执行扫描（支持取消检查）
                result = run_bandit_scan(target_path, cancel_check=is_cancelled)

                # 检查是否被取消
                if is_cancelled():
                    task.status = 'cancelled'
                    task.result = {"message": "Task cancelled by user"}
                    send_progress(task_id, -1, "任务已取消")
                else:
                    # 关键：设置状态为 completed
                    task.status = 'completed'
                    task.result = result
                    send_progress(task_id, 100, "扫描完成")

                task.completed_at = datetime.utcnow()
                db.session.commit()

                # 如果是 ZIP 上传的任务，清理临时目录
                if target_path.startswith('/app/uploads'):
                    shutil.rmtree(target_path, ignore_errors=True)

            except Exception as e:
                app.logger.error(f"Scan task {task_id} failed: {e}")
                task.status = 'failed'
                task.result = {"error": str(e)}
                task.completed_at = datetime.utcnow()
                db.session.commit()
                send_progress(task_id, -1, f"失败: {str(e)}")

    threading.Thread(target=_run, daemon=True).start()