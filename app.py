from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime
import hashlib
import hmac
import os
import json

app = Flask(__name__)
CORS(app)
db = Database()

# Constants
REFERRAL_BONUS = 5.0
TASK_CREATION_COST = 2.0
TASK_COMPLETION_REWARD = 10.0

def verify_telegram_webapp(data, hash_str, bot_token):
    """Verify Telegram WebApp data"""
    data_check_string = '&'.join(f"{k}={v}" for k, v in sorted(data.items()) if k != 'hash')
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_str

@app.route('/')
def index():
    """Serve the Mini App frontend"""
    return render_template('index.html')

@app.route('/api/user', methods=['POST'])
def get_user():
    """Get or create user from Telegram data"""
    try:
        data = request.json
        init_data = data.get('initData', '')
        
        # Parse initData
        params = {}
        for pair in init_data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
        
        # Verify (in production, verify with bot token)
        telegram_id = int(params.get('user', '{}').split('"id":')[1].split(',')[0]) if 'user' in params else None
        if not telegram_id:
            return jsonify({'error': 'Invalid user data'}), 400
        
        # Parse user JSON
        user_data = json.loads(params.get('user', '{}'))
        telegram_id = user_data.get('id')
        username = user_data.get('username')
        first_name = user_data.get('first_name')
        
        # Get or create user
        user = db.get_or_create_user(telegram_id, username, first_name)
        
        # Check if user is admin
        is_admin = str(user.telegram_id) in ADMIN_TELEGRAM_IDS or user.is_admin
        
        return jsonify({
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'coins': user.coins,
            'referral_code': user.referral_code,
            'is_admin': is_admin,
            'level': user.level or 1,
            'total_earned': user.total_earned or 0.0,
            'tasks_completed': user.tasks_completed or 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get tasks for user"""
    try:
        telegram_id = int(request.args.get('telegram_id'))
        user = db.get_or_create_user(telegram_id=telegram_id)
        
        session = db.get_session()
        try:
            from database import Task, User
            # Get assigned tasks
            assigned_tasks = session.query(Task).filter_by(
                assigned_to=user.id, 
                completed=False
            ).all()
            
            # Get available tasks (not assigned)
            available_tasks = session.query(Task).filter_by(
                assigned_to=None,
                completed=False
            ).all()
            
            # Get created tasks
            created_tasks = session.query(Task).filter_by(
                created_by=user.id
            ).order_by(Task.created_at.desc()).limit(20).all()
            
            def task_to_dict(task):
                creator = session.query(User).filter_by(id=task.created_by).first()
                assignee = session.query(User).filter_by(id=task.assigned_to).first() if task.assigned_to else None
                return {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'reward_coins': task.reward_coins,
                    'completed': task.completed,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'creator_name': creator.first_name if creator else 'Unknown',
                    'assignee_name': assignee.first_name if assignee else None,
                    'assigned_to': task.assigned_to,
                    'created_by': task.created_by
                }
            
            return jsonify({
                'assigned': [task_to_dict(t) for t in assigned_tasks],
                'available': [task_to_dict(t) for t in available_tasks],
                'created': [task_to_dict(t) for t in created_tasks]
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """Create a new task - Admin only"""
    try:
        data = request.json
        telegram_id = int(data.get('telegram_id'))
        title = data.get('title')
        description = data.get('description', '')
        reward_coins = float(data.get('reward_coins', TASK_COMPLETION_REWARD))
        
        user = db.get_or_create_user(telegram_id=telegram_id)
        
        # Check if user is admin
        is_admin = str(user.telegram_id) in ADMIN_TELEGRAM_IDS or user.is_admin
        if not is_admin:
            return jsonify({'error': 'Only admins can create tasks!'}), 403
        
        session = db.get_session()
        try:
            from database import Task, Transaction
            task = Task(
                title=title,
                description=description,
                created_by=user.id,
                reward_coins=reward_coins
            )
            session.add(task)
            
            # Admins don't pay for task creation
            # user.coins -= TASK_CREATION_COST
            # transaction = Transaction(
            #     user_id=user.id,
            #     amount=-TASK_CREATION_COST,
            #     transaction_type='task_creation',
            #     description=f'Created task: {title}'
            # )
            # session.add(transaction)
            session.commit()
            session.refresh(task)
            
            return jsonify({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'reward_coins': task.reward_coins
                },
                'new_balance': user.coins
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/assign', methods=['POST'])
def assign_task():
    """Assign a task to a user"""
    try:
        data = request.json
        task_id = int(data.get('task_id'))
        assignee_telegram_id = int(data.get('assignee_telegram_id'))
        assigner_telegram_id = int(data.get('assigner_telegram_id'))
        
        session = db.get_session()
        try:
            from database import Task
            task = session.query(Task).filter_by(id=task_id).first()
            assignee = db.get_or_create_user(telegram_id=assignee_telegram_id)
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            if task.completed:
                return jsonify({'error': 'Task already completed'}), 400
            
            task.assigned_to = assignee.id
            session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Task assigned to {assignee.first_name}'
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    """Complete a task"""
    try:
        data = request.json
        task_id = int(data.get('task_id'))
        telegram_id = int(data.get('telegram_id'))
        
        user = db.get_or_create_user(telegram_id=telegram_id)
        session = db.get_session()
        try:
            from database import Task, User
            task = session.query(Task).filter_by(id=task_id).first()
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            if task.completed:
                return jsonify({'error': 'Task already completed'}), 400
            
            if task.assigned_to != user.id:
                return jsonify({'error': 'Task not assigned to you'}), 403
            
            task.completed = True
            task.completed_at = datetime.utcnow()
            session.commit()
            
            # Give reward
            new_balance = db.add_coins(
                user.id,
                task.reward_coins,
                'task_reward',
                f'Completed task: {task.title}'
            )
            
            # Update user stats
            from database import User
            db_user = session.query(User).filter_by(id=user.id).first()
            if db_user:
                old_level = db_user.level or 1
                db_user.tasks_completed = (db_user.tasks_completed or 0) + 1
                db_user.total_earned = (db_user.total_earned or 0.0) + task.reward_coins
                
                # Level up system (every 10 tasks = 1 level)
                new_level = (db_user.tasks_completed // 10) + 1
                if new_level > (db_user.level or 1):
                    db_user.level = new_level
                
                session.commit()
                level_up = new_level > old_level
            else:
                new_level = 1
                level_up = False
            
            return jsonify({
                'success': True,
                'reward': task.reward_coins,
                'new_balance': new_balance,
                'level_up': level_up,
                'new_level': new_level,
                'tasks_completed': db_user.tasks_completed if db_user else 0
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """Search users by username or telegram_id"""
    try:
        query = request.args.get('q', '')
        session = db.get_session()
        try:
            from database import User
            users = session.query(User).filter(
                (User.username.contains(query)) | 
                (User.first_name.contains(query)) |
                (User.telegram_id == query if query.isdigit() else False)
            ).limit(10).all()
            
            return jsonify([{
                'id': u.id,
                'telegram_id': u.telegram_id,
                'username': u.username,
                'first_name': u.first_name,
                'coins': u.coins
            } for u in users])
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard"""
    try:
        session = db.get_session()
        try:
            from database import User
            top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()
            
            return jsonify([{
                'rank': i + 1,
                'first_name': u.first_name or u.username or f'User {u.telegram_id}',
                'coins': u.coins
            } for i, u in enumerate(top_users)])
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get user transactions"""
    try:
        telegram_id = int(request.args.get('telegram_id'))
        user = db.get_or_create_user(telegram_id=telegram_id)
        
        session = db.get_session()
        try:
            from database import Transaction
            transactions = session.query(Transaction).filter_by(
                user_id=user.id
            ).order_by(Transaction.created_at.desc()).limit(20).all()
            
            return jsonify([{
                'id': t.id,
                'amount': t.amount,
                'type': t.transaction_type,
                'description': t.description,
                'created_at': t.created_at.isoformat() if t.created_at else None
            } for t in transactions])
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/referral', methods=['GET'])
def get_referral():
    """Get referral info"""
    try:
        telegram_id = int(request.args.get('telegram_id'))
        user = db.get_or_create_user(telegram_id=telegram_id)
        
        session = db.get_session()
        try:
            from database import User
            referrals_count = session.query(User).filter_by(referred_by=user.id).count()
            
            return jsonify({
                'referral_code': user.referral_code,
                'referrals_count': referrals_count,
                'bonus_per_referral': REFERRAL_BONUS
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tap', methods=['POST'])
def tap_earn():
    """Handle tap-to-earn"""
    try:
        data = request.json
        telegram_id = int(data.get('telegram_id'))
        coins = float(data.get('coins', 1.0))
        
        user = db.get_or_create_user(telegram_id=telegram_id)
        
        # Add coins from tap
        new_balance = db.add_coins(
            user.id,
            coins,
            'tap_reward',
            f'Tap to earn: {coins} coins'
        )
        
        return jsonify({
            'success': True,
            'coins_earned': coins,
            'new_balance': new_balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

