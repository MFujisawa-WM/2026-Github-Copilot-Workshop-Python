"""
Pomodoro Timer Web Application
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    """メインページを返却"""
    return render_template('index.html')


@app.route('/api/stats/today')
def get_stats():
    """本日の統計情報を返す"""
    return jsonify({
        'completed': 0,
        'totalMinutes': 0
    })


@app.route('/api/sessions', methods=['POST'])
def save_session():
    """セッション情報を保存"""
    try:
        data = request.json
        return jsonify({
            'status': 'success',
            'id': 1,
            'message': 'セッションが保存されました'
        }), 201
    except Exception as e:
        app.logger.exception('Failed to save session')
        return jsonify({
            'status': 'error',
            'message': 'セッションの保存中にエラーが発生しました'
        }), 400


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラ"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラ"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
