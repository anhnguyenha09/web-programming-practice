from flask import Flask, request, jsonify, render_template, flash
# import cac thu vien gom flask (backend), jsonify (de tra ve json), request (de nhan cac method), render_template(de render html), flash (de hien thi thong bao loi tren giao dien)
import sqlite3 # thu vien tuong tac voi csdl sqlite
import json # thu vien xu li json

app = Flask(__name__) # khai bao bien app = Flask(__name__) de khoi tao ung dung flask

# bien tro toi co so du lieu
DB = 'luyentapcki.db'

def get_db_connection(): # dinh nghia ham ket noi csdl
    conn = sqlite3.connect(DB) # bien conn su dung tvien sqlite3 de ket noi toi csdl da khai bao
    conn.row_factory = sqlite3.Row # row_factory la mot thuoc tinh cua ket noi, sqlite3.Row cho phep truy cap du lieu bang ten cot thay vi chi so
    return conn # tra ve ket noi da duoc cau hinh de truy cap du lieu bang ten cot

def init_db(): # dinh nghia ham khoi tao csdl
    conn = get_db_connection() # bien conn tai day su dung ham ket noi csdl (van tra ve conn)
    cur = conn.cursor() # khai bao bien cur de thuc hien cac lenh sql, cursor la mot doi tuong cho phep thuc thi cac lenh sql va truy cap ket qua

    # o day ta hieu conn la ket noi den csdl, cur la doi tuong thuc thi thao tac trong csdl

    # do do, bien cur co the thuc thi (execute) cac lenh sql nhu tao bang, chen du lieu, truy van du lieu, v.v.
    cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    class_id INTEGER
                )
            ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL)
                ''')
    conn.commit() # commit la lenh de luu cac thay doi da thuc hien vao csdl, neu khong commit thi cac thay doi se khong duoc luu va se mat khi dong ket noi


    with open('users.json', 'r', encoding='utf-8') as f: # mo file users.json de doc du lieu, 'r' la che do doc, encoding='utf-8' de dam bao doc du lieu dung dinh dang utf-8
        users = json.load(f) # json.load de doc du lieu tu file json va chuyen doi no thanh doi tuong python (trong truong hop nay la mot danh sach cac dict, moi dict dai dien cho mot user voi cac key la username va email)
    # f o day la bien dai dien cho file da mo, users la bien chua du lieu da doc tu file json
    for u in users: # lap qua tung user (dai dien la bien u) trong danh sach users de chen du lieu vao csdl
        cur.execute( # bien con tro thuc thi lenh sql
            'INSERT INTO users (username, email, class_id) VALUES (?, ?, ?)', # lenh sql de chen du lieu vao bang users, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do
            (u['username'], u['email'], u['class_id']) # gia tri thuc te duoc truyen vao de thay the cac dau hoi ?, o day la username, email va class_id cua user hien tai (u) trong vong lap 
            # u['username'] truy cap gia tri cua key 'username' trong dict u, tuong tu cho email va class_id
        )
    conn.commit()
    conn.close()

@app.route('/') # dinh nghia route cho trang chu, khi nguoi dung truy cap vao duong dan '/' thi ham index se duoc thuc thi
def index():
    return "Nguyen Ha Anh beo" # tra ve mot chuoi don gian khi nguoi dung truy cap vao trang chu

@app.route('/users', methods=['GET']) # dinh nghia route cho duong dan '/users', chi chap nhan phuong thuc GET, khi nguoi dung truy cap vao duong dan nay voi phuong thuc GET thi ham get_users se duoc thuc thi
def get_users():
    conn = get_db_connection() # ket noi toi csdl de truy van du lieu
    cur = conn.cursor() # tao doi tuong cursor de thuc thi lenh sql
    cur.execute('SELECT * FROM users') # thuc thi lenh sql de lay tat ca du lieu tu bang users
    users = cur.fetchall() # lay tat ca cac hang duoc tra ve tu lenh sql va luu vao bien users, fetchall() tra ve mot danh sach cac hang, moi hang duoc dai dien boi mot doi tuong sqlite3.Row (do ta da cau hinh row_factory truoc do), ban co the truy cap du lieu trong moi hang bang ten cot (vd: row['username'])
    conn.commit() # commit la lenh de luu cac thay doi da thuc hien vao csdl, trong truong hop nay ta khong thuc hien thay doi nao tren csdl, nhung van goi commit (cho quen tay)
    conn.close() # dong ket noi
    
    #tra ve json
    return jsonify([dict(row) for row in users]) # jsonify de chuyen doi du lieu thanh dinh dang json de tra ve cho client, [dict(row) for row in users] la mot list comprehension de tao ra mot danh sach moi, moi phan tu trong danh sach moi la mot dict duoc tao ra tu doi tuong row (moi row dai dien cho mot user), dict(row) chuyen doi doi tuong row thanh mot dict, do do ta co mot danh sach cac dict, moi dict dai dien cho mot user voi cac key la ten cot (vd: 'username', 'email') va gia tri la gia tri tuong ung cua cot do trong hang do
    # dict(row) chuyen doi doi tuong row thanh mot dict, do do ta co mot danh sach cac dict, moi dict dai dien cho mot user voi cac key


@app.route('/users/<int:user_id>', methods=['DELETE']) # dinh nghia route cho duong dan '/users', chi chap nhan phuong thuc DELETE, khi nguoi dung gui mot yeu cau DELETE den duong dan nay thi ham delete_user se duoc thuc thi
#<int:user_id> la mot tham so duoc truyen vao ham delete_users, user_id se duoc chuyen doi sang kieu int va truyen vao ham de su dung trong lenh sql
def delete_user(user_id):
    conn = get_db_connection() # ket noi toi csdl
    cur = conn.cursor() # tao doi tuong cursor de thuc thi lenh sql
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,)) # thuc thi lenh sql de xoa user co cot id bang user_id, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (user_id,) la mot tuple chi chua mot phan tu (user_id), do do phai co dau phay sau user_id de tao ra mot tuple
    conn.commit() #commit de luu thay doi vao csdl
    conn.close() #dong ket noi
    return jsonify({'message': f'Da xoa user co id = {user_id}'})
    # tra ve mot dict duoc chuyen doi sang json, dict nay chua mot key 'message' voi gia tri la mot chuoi thong bao da xoa user co id = user_id (su dung f-string de chen gia tri user_id vao chuoi)
    # cai chu f la f-string (formatted string) là cách viết chuỗi trong Python giúp bạn chèn biến hoặc biểu thức trực tiếp vào trong string một cách gọn và dễ đọc.

@app.route('/users', methods=['POST']) # dinh nghia route cho duong dan '/users', chi chap nhan phuong thuc POST, khi nguoi dung gui mot yeu cau POST den duong dan nay thi ham add_user se duoc thuc thi
def add_user():
    data = request.get_json() # request.get_json() de lay du lieu duoc gui len tu client va chuyen doi no thanh mot dict python, data se tro thanh bien chua dict duoc truyen vao tu client
    username = data.get('username') # lay gia tri cua key 'username' trong dict data, luu vao bien username
    email = data.get('email') # lay gia tri cua key 'email' trong dict data, luu vao bien email
    class_id = data.get('class_id') # lay gia tri cua key 'class_id' trong dict data, luu vao bien class_id

    conn = get_db_connection() #ket noi toi csdl
    cur = conn.cursor() #tao doi tuong cursor de thuc thi lenh sql
    cur.execute('INSERT INTO users (username, email, class_id) VALUES (?, ?, ?)', (username, email, class_id))
    # thuc thi lenh sql de chen du lieu vao bang users cho cot username va email, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (username, email) la mot tuple chua gia tri se duoc truyen vao de thay the cac dau hoi ?
    conn.commit() #commit de luu thay doi vao csdl
    
    new_user_id = cur.lastrowid # lastrowid la mot thuoc tinh cua cursor, no tra ve id cua hang moi duoc chen vao bang (trong truong hop nay la id cua user moi duoc them vao)
    conn.close() #dong ket noi
    return jsonify({'message': f'Da them user moi voi id = {new_user_id}'})

@app.route('/users/<int:user_id>', methods=['PUT']) # dinh nghia route cho duong dan '/users', chi chap nhan phuong thuc PUT, khi nguoi dung gui mot yeu cau PUT den duong dan nay thi ham update_user se duoc thuc thi
def update_user(user_id):
    data = request.get_json() # lay du lieu duoc gui len tu client va chuyen doi no thanh 1 dict python, data se tu JSON tro thanh bien chua dict duoc truyen vao tu client

    # lam cach moi nhe, ko can phai lay tung gia tri username, email nhu o ham add_user, ma ta co the truyen thang dict data vao lenh sql de cap nhat du lieu
    conn = get_db_connection() # ket noi toi csdl
    cur = conn.cursor() # tao doi tuong cursor de thuc thi lenh sql
    cur.execute('''
                UPDATE users 
                SET username = ?, email = ?, class_id = ? 
                WHERE id = ?
                ''', # lenh sql de cap nhat du lieu trong bang users, set username = ?, email = ? de cap nhat gia tri cua cot username va email, where id = ? de xac dinh user can cap nhat theo id, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do
                (data.get('username'), data.get('email'), data.get('class_id'), user_id) # hoac co the truyen thang dict data vao lenh sql, data['username'] truy cap gia tri cua key 'username' trong dict data, tuong tu cho email, user_id la id cua user can cap nhat, da khai bao trong ham
    )

    conn.commit() # commit de luu thay doi vao csdl
    conn.close() # dong ket noi
    return jsonify({'message': f'Da cap nhat user co id = {user_id}'})

# kiem tra user ton tai theo email va username
@app.route('/users/check', methods=['GET']) # dinh nghia route cho duong dan '/users/check', chi chap nhan phuong thuc GET, khi nguoi dung gui mot yeu cau GET den duong dan nay thi ham check_user se duoc thuc thi
def check_user():
    email = request.args.get('email') # lay gia tri cua tham so email trong chuoi truy van, luu vao bien email
    username = request.args.get('username') # lay gia tri cua tham so username trong chuoi truy van, luu vao bien username

    conn = get_db_connection() # ket noi toi csdl
    cur = conn.cursor() # tao doi tuong cursor de thuc thi lenh sql
    cur.execute('SELECT * FROM users WHERE email = ? OR username = ?', (email, username)) # thuc thi lenh sql de kiem tra xem co user nao co email hoac username trung voi gia tri duoc truyen vao hay khong, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (email, username) la mot tuple chua gia tri se duoc truyen vao de thay the cac dau hoi ?
    user = cur.fetchone() #lay hang dau tien duoc tra ve tu lenh sql, fetchone() tra ve mot doi tuong sqlite3.Row dai dien cho user neu co, neu khong co user nao trung thi tra ve None

    #ko co thay doi j ve csdl nen ko can conn.commit()
    conn.close() 

    if user: # neu user khac None (co user trung email hoac username)
        return jsonify({'exists': True, 'user': dict(user)}) # tra ve mot dict duoc chuyen doi sang json, dict nay chua key 'exists' voi gia tri True de bao user da ton tai, va key 'user' voi gia tri la mot dict duoc tao ra tu doi tuong user (trong truong hop nay la mot sqlite3.Row), dict(user) chuyen doi doi tuong user thanh mot dict de co the truyen vao json
    else: # neu user la None (khong co user nao trung)
        return jsonify({'exists': False, 'message': 'Khong tim thay user'})
    
# tim kiem theo chuoi doi voi username hoac email trong truy van
@app.route('/users/search', methods=['GET']) # dinh nghia route cho duong dan '/users/search', chi chap nhan phuong thuc GET, khi nguoi dung gui mot yeu cau GET den duong dan nay thi ham search_users se duoc thuc thi
def search_users():
    keyword = request.args.get('q', '') # lay gia tri cua tham so q trong chuoi truy van, neu khong co tham so q thi tra ve chuoi rong, luu vao bien keyword
    #q la tham so trong url, thuong chua tu khoa tim kiem
    pattern = f'%{keyword}%' # tao pattern de su dung trong lenh sql, % la ky tu wildcard trong sql, do do pattern se tim kiem cac username hoac email chua chuoi keyword o bat ky vi tri nao

    conn = get_db_connection()
    cur = conn.cursor()
    results = cur.execute('SELECT * FROM users WHERE username LIKE ? OR email LIKE ?', (pattern, pattern)).fetchall() # thuc thi lenh sql de tim kiem user co username hoac email chua chuoi keyword, su dung LIKE de tim kiem theo pattern, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (pattern, pattern) la mot tuple chua gia tri se duoc truyen vao de thay the cac dau hoi ?, o day ca username va email deu su dung cung mot pattern
    conn.close()

    #tra ve kqua json
    return jsonify([dict(row) for row in results]) # tra ve mot danh sach cac dict duoc chuyen doi sang json, moi dict dai dien cho mot user trong ket qua tim kiem, dict(row) chuyen doi doi tuong row thanh mot dict de co the truyen vao json

# lay danh sach user theo ClassID
@app.route('/users/class/<int:class_id>', methods=['GET'])
def get_users_by_class(class_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # user_class = cur.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone() 
    # # lay thong tin lop hoc theo class_id, neu khong tim thay thi user_class se la None
    # if not user_class:
    #     conn.close()
    #     return jsonify({'message': f'Khong tim thay lop hoc co id = {class_id}'})
    
    # else:
    users = cur.execute('SELECT * FROM users WHERE class_id = ?', (class_id,)).fetchall()
        # lay danh sach user trong bang co cot class_id bang class_id, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (class_id,) la mot tuple chua gia tri se duoc truyen vao de thay the cac dau hoi ?, o day la mot tuple voi mot phan tu duy nhat la class_id
    conn.close()

    return jsonify({'users': [dict(user) for user in users]})
        # tra ve mot dict duoc chuyen doi sang json, dict nay chua key 'users' voi gia tri la mot danh sach cac dict dai dien cho user trong lop hoc do, va key 'class' voi gia tri la mot dict dai dien cho lop hoc do, dict(user_class) chuyen doi doi tuong user_class thanh mot dict de co the truyen vao json

# them 1 loat user 
@app.route('/users/batch', methods=['POST'])
def add_users_batch():
    data = request.get_json() # lay du lieu duoc gui len tu client va chuyen doi no thanh 1 dict python, data se tu JSON tro thanh bien chua dict

    conn = get_db_connection()
    cur = conn.cursor()

    inserted_users = [] # tao mot danh sach rong de luu tru thong tin cac user moi duoc them vao

    for u in data:
        cur.execute('INSERT INTO users (username, email, class_id) VALUES (?, ?, ?)', (u.get('username'), u.get('email'), u.get('class_id')))
        # thuc thi lenh sql de chen du lieu vao bang users cho cot username, email va class_id, su dung dau hoi ? de thay the bang gia tri thuc te se truyen vao sau do, (u['username'], u['email'], u['class_id']) la mot tuple chua gia tri se duoc truyen vao de thay the cac dau hoi ?, u['username'] truy cap gia tri cua key 'username' trong dict u, tuong tu cho email va class_id
        inserted_users.append({'id': cur.lastrowid, 'username': u.get('username'), 'email': u.get('email'), 'class_id': u.get('class_id')})
        # sau khi chen du lieu vao csdl, ta them mot dict dai dien cho user moi duoc them vao danh sach inserted_users, dict nay chua key 'id' voi gia tri la id cua user moi duoc them vao (cur.lastrowid), va cac key 'username', 'email', 'class_id' voi gia tri tuong ung duoc lay tu dict u
        conn.commit() # commit de luu thay doi vao csdl sau moi lan chen du lieu, de dam bao rang se ko bi lock database ==> neu nhu 1 user chua dc insert xong ma da co user khac cung luc cung insert, neu ko commit sau moi lan chen thi se bi lock database va khong the chen du lieu cho cac user khac cho den khi lenh sql truoc do duoc commit va giai phong lock
    conn.commit()
    conn.close()

    return jsonify({'message': f'Da them {len(inserted_users)} user moi', 'users': inserted_users})
    # tra ve mot dict duoc chuyen doi sang json, dict nay chua key 'message' voi gia tri la mot chuoi thong bao da them bao nhieu user moi, va key 'users' voi gia tri la mot danh sach cac dict dai dien cho user moi duoc them vao, moi dict chua id, username va email cua user do

#route hien thi giao dien html // cai nay t luyen them thoi
@app.route('/view/<int:user_id>', methods=['GET'])
def view(user_id): # dinh nghia route cho duong dan '/view/<int:user_id>', chi chap nhan phuong thuc GET, khi nguoi dung truy cap vao duong dan nay voi mot user_id thi ham view se duoc thuc thi, user_id se duoc chuyen doi sang kieu int va truyen vao ham de su dung trong lenh sql
    conn = get_db_connection()
    cur = conn.cursor()

    users = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchall() # lay tat ca du lieu tu bang users tmdk, fetchall() tra ve mot danh sach cac hang, moi hang duoc dai dien boi mot doi tuong sqlite3.Row (do ta da cau hinh row_factory truoc do), ban co the truy cap du lieu trong moi hang bang ten cot (vd: row['username'])
    conn.close() # thuc ra fetchone cung duoc neu chi muon lay mot user, nhung de cho de code va de sau nay co the thay doi de lay nhieu user cung luc thi ta dung fetchall() de luu vao bien users la mot danh sach cac user (duoi dang sqlite3.Row), neu chi co mot user thi danh sach se chi chua mot phan tu, neu khong co user nao trung thi danh sach se rong

    return jsonify([dict(row) for row in users]) # tra ve mot danh sach cac dict duoc chuyen doi sang json, moi dict dai dien cho mot user trong bang users, dict(row) chuyen doi doi tuong row thanh mot dict de co the truyen vao json

    #return render_template('index.html', users=users) 
    
    # render_template de render file html, o day la index.html, va truyen bien users vao file html de su dung trong do, users se tro thanh mot danh sach cac doi tuong sqlite3.Row dai dien cho user, ban co the truy cap du lieu trong moi row bang ten cot (vd: row['username']) trong file html
    #users ben phai la bien duoc dinh nghia trong file app.py, users ben trai la bien trong html
    # cu the, trong html se ghi nhu the nay:
    # {% for user in users %}
    #     <p>{{ user['username'] }} - {{ user['email'] }}</p>
    # {% endfor %}
    # do do, khi render html, no se lap qua tung user trong danh sach users
    # va hien thi username va email cua user do trong the p, su dung {{ }} de chen gia tri vao html

if __name__ == '__main__':
    init_db() # khoi tao csdl khi chay ung dung (đây là tính năng của sqlite là tự tạo csdl nếu ch có), ham init_db se tao bang users neu chua co, va chen du lieu tu file users.json vao bang users
    app.run(debug=True, port=5000) # chay ung dung flask, debug=True de cho phep tu dong tai lai khi co thay doi trong code va hien thi loi chi tiet khi co loi xay ra
    # port=5000 de chay ung dung tren cong 5000
    