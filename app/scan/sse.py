import queue
import json
from flask import Response

class ProgressQueue:
    _queues = {}

    @classmethod
    def get(cls, task_id):
        if task_id not in cls._queues:
            cls._queues[task_id] = queue.Queue()
        return cls._queues[task_id]

    @classmethod
    def put(cls, task_id, message):
        if task_id in cls._queues:
            cls._queues[task_id].put(message)
        else:
            q = queue.Queue()
            q.put(message)
            cls._queues[task_id] = q

    @classmethod
    def cleanup(cls, task_id):
        if task_id in cls._queues:
            del cls._queues[task_id]

def stream_progress(task_id):
    q = ProgressQueue.get(task_id)
    try:
        yield f"data: {json.dumps({'status': 'connected', 'progress': 0})}\n\n"
        while True:
            try:
                data = q.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get('status') in ('completed', 'failed'):
                    break
            except queue.Empty:
                yield ": heartbeat\n\n"
    finally:
        ProgressQueue.cleanup(task_id)

def send_progress(task_id, progress, message=None):
    data = {"progress": progress, "message": message or f"进度: {progress}%"}
    ProgressQueue.put(task_id, data)