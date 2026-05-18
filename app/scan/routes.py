import csv
import json
from io import StringIO
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from ..models import ScanTask, db
from .tasks import start_async_scan
from .comparator import compare_scan_results
from .snippet import get_code_snippet
from .upload import process_zip_upload
from .sse import stream_progress

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/start', methods=['POST'])
@jwt_required()
def start_scan():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'target_path' not in data:
        return jsonify({"msg": "Missing target_path"}), 400
    target = data['target_path']
    task_name = data.get('task_name', f"Scan_{target.replace('/', '_')}")
    task = ScanTask(
        user_id=int(user_id),
        task_name=task_name,
        target_path=target,
        status='pending'
    )
    db.session.add(task)
    db.session.commit()
    start_async_scan(task.id, target)
    return jsonify({"task_id": task.id, "status": "pending"}), 202

@scan_bp.route('/result/<int:task_id>', methods=['GET'])
@jwt_required()
def get_result(task_id):
    user_id = get_jwt_identity()
    task = ScanTask.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    return jsonify({
        "task_id": task.id,
        "task_name": task.task_name,
        "status": task.status,
        "target_path": task.target_path,
        "result": task.result,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    })

@scan_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = ScanTask.query.filter_by(user_id=int(user_id)).order_by(
        ScanTask.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'tasks': [{
            'id': t.id,
            'task_name': t.task_name,
            'target_path': t.target_path,
            'status': t.status,
            'created_at': t.created_at.isoformat(),
            'completed_at': t.completed_at.isoformat() if t.completed_at else None
        } for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@scan_bp.route('/cancel/<int:task_id>', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    user_id = get_jwt_identity()
    task = ScanTask.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    if task.status == 'completed':
        return jsonify({"msg": "Task already completed"}), 400
    if task.status == 'cancelled':
        return jsonify({"msg": "Task already cancelled"}), 400
    task.cancel_requested = True
    if task.status == 'pending':
        task.status = 'cancelled'
        db.session.commit()
        return jsonify({"msg": "Task cancelled (was pending)"}), 200
    db.session.commit()
    return jsonify({"msg": "Cancellation requested"}), 200

@scan_bp.route('/export/<int:task_id>', methods=['GET'])
@jwt_required()
def export_csv(task_id):
    user_id = get_jwt_identity()
    task = ScanTask.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task or task.status != 'completed':
        return jsonify({"msg": "Task not found or not completed"}), 404
    results = task.result.get('results', []) if task.result else []
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Line', 'Severity', 'Test Name', 'Description', 'Filename'])
    for issue in results:
        writer.writerow([
            issue.get('line_number', ''),
            issue.get('severity', ''),
            issue.get('test_name', ''),
            issue.get('issue_text', ''),
            issue.get('filename', '')
        ])
    response = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=scan_{task_id}.csv'
    return response

@scan_bp.route('/compare/<int:id1>/<int:id2>', methods=['GET'])
@jwt_required()
def compare_scans(id1, id2):
    user_id = get_jwt_identity()
    task1 = ScanTask.query.filter_by(id=id1, user_id=int(user_id)).first()
    task2 = ScanTask.query.filter_by(id=id2, user_id=int(user_id)).first()
    if not task1 or not task2:
        return jsonify({"msg": "Task not found"}), 404
    if task1.status != 'completed' or task2.status != 'completed':
        return jsonify({"msg": "Both scans must be completed"}), 400
    result1 = task1.result if task1.result else {"results": []}
    result2 = task2.result if task2.result else {"results": []}
    comparison = compare_scan_results(result1, result2)
    return jsonify(comparison)

@scan_bp.route('/snippet', methods=['GET'])
@jwt_required()
def snippet():
    file_path = request.args.get('file')
    line = request.args.get('line', type=int)
    if not file_path or not line:
        return jsonify({"error": "Missing file or line"}), 400
    result = get_code_snippet(file_path, line)
    return jsonify(result)

@scan_bp.route('/upload_zip', methods=['POST'])
@jwt_required()
def upload_zip():
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({"msg": "Invalid file"}), 400
    try:
        extract_path = process_zip_upload(file, extract_to='/app/uploads')
        user_id = get_jwt_identity()
        task = ScanTask(
            user_id=int(user_id),
            task_name=f"ZIP_Scan_{file.filename}",
            target_path=extract_path,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        start_async_scan(task.id, extract_path)
        return jsonify({"task_id": task.id, "status": "pending"}), 202
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@scan_bp.route('/progress/<int:task_id>', methods=['GET'])
def progress(task_id):
    token = request.args.get('token')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
    except:
        return jsonify({"msg": "Invalid token"}), 401
    task = ScanTask.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    return Response(stream_progress(task_id), mimetype='text/event-stream')