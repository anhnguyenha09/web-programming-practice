from flask import Flask, jsonify, render_template, flash, request
import sqlite3
import json

app = Flask(__name__)

DB = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        class_id INTEGER)
    ''')
    conn.commit()

    #sau khi tao bang va commit, nhap csdl

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for u in data:
        cur.execute('INSERT INTO user (username, email, class_id) VALUES (?,?,?)', (u['username'], u['email'], u['class_id']))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return 'Nguyen Ha Anh bel'

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    SELECT * from user''')
    users = cur.fetchall()

    conn.close()
    return jsonify([dict(row) for row in users])

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    DELETE FROM user WHERE id = ?''', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Da xoa user co id la {user_id}'})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO user (username, email, class_id) VALUES (?,?,?)''', (data['username'], data['email'], data.get('class_id')))

    new_user_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'message': f'Da them user co id la {new_user_id}'})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    UPDATE user SET username = ?, email = ?, class_id = ? WHERE id = ?''',
                (data.get('username'), data.get('email'), data.get('class_id'), user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Da cap nhat user co id la {user_id}'})

@app.route('/users/class/<int:class_id>', methods=['GET'])
def get_user_by_class_id(class_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    SELECT * from user WHERE class_id = ?''', (class_id,))
    users = cur.fetchall()
    conn.close()
    return jsonify({'message': f'Danh sach cac user co ma lop la {class_id}', 'users': [dict(row) for row in users]})

@app.route('/users/check', methods=['GET'])
def check_user():
    username = request.args.get('username')
    email = request.args.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    SELECT * from user WHERE username = ? OR email = ?''', (username, email))

    users = cur.fetchall()
    conn.close()

    if not users:
        return jsonify({'message': 'Khong ton tai user'})
    else:
        return jsonify({'message': 'Co ton tai user sau day: ', 'users': [dict(row) for row in users]})

@app.route('/users/batch', methods=['POST'])
def batch_users():
    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()

    inserted_users = []

    for user in data:
        cur.execute('''
        INSERT INTO user (username, email, class_id) VALUES (?,?,?)''',
                    (user['username'], user['email'], user.get('class_id')))
        #append dict user?
        inserted_users.append({'id': cur.lastrowid, 'username': user['username'], 'email': user['email'], 'class_id': user.get('class_id')})
        conn.commit()
    conn.commit()
    conn.close()

    return jsonify({'message': f'Da them {len(inserted_users)} user moi', 'users': inserted_users}) # cho nay dien [dict] / list (hien tai la list)

@app.route('/users/search', methods=['GET'])
def search_user():
    keyword = request.args.get('q', '')
    pattern = f'%{keyword}%'

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    SELECT * from user WHERE username LIKE ? or email LIKE ? or class_id LIKE ?''',
                (pattern, pattern, pattern))

    users = cur.fetchall()
    conn.close()
    if not users:
        return jsonify({'message': 'Khong ton tai user'})
    else:
        return jsonify({'message': 'Danh sach user tim duoc:',
                        'users': [dict(row) for row in users]})

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)




