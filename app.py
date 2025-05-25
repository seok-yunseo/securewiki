from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

import init_db

app = Flask(__name__)

# ✅ DB 연결 함수
def get_db_connection():
    conn = sqlite3.connect('wiki.db')
    conn.row_factory = sqlite3.Row
    return conn

# ✅ 메인 페이지
@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('q', '')
    conn = get_db_connection()
    if keyword:
        query = "SELECT * FROM terms WHERE title LIKE ? OR content LIKE ?"
        terms = conn.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()
    else:
        terms = conn.execute("SELECT * FROM terms").fetchall()
    conn.close()
    return render_template('index.html', terms=terms, keyword=keyword)

# ✅ 용어 보기
@app.route('/term/<title>', methods=['GET'])
def view_term(title):
    conn = get_db_connection()
    term = conn.execute("SELECT * FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return render_template('view_term.html', term=term)
    else:
        return f"❌ '{title}' 용어가 존재하지 않습니다.", 404

# ✅ 용어 추가
@app.route('/add', methods=['GET', 'POST'])
def add_term():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        editor = request.form['editor']
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO terms (title, content, category, author, last_editor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, category, editor, editor, datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('view_term', title=title))
    return render_template('add_term.html')

# ✅ 용어 수정
@app.route('/edit/<title>', methods=['GET', 'POST'])
def edit_term(title):
    conn = get_db_connection()
    if request.method == 'POST':
        new_content = request.form['new_content']
        editor = request.form.get('editor', 'unknown')
        conn.execute('''
            UPDATE terms
            SET content = ?, last_editor = ?, updated_at = ?
            WHERE title = ?
        ''', (new_content, editor, datetime.now(), title))
        conn.commit()
        conn.close()
        return redirect(url_for('view_term', title=title))
    term = conn.execute("SELECT content FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return render_template('edit_term.html', title=title, content=term['content'])
    else:
        return f"❌ '{title}' 용어가 존재하지 않습니다.", 404

# ✅ API: 모든 용어 조회
@app.route("/api/terms", methods=["GET"])
def api_get_terms():
    conn = get_db_connection()
    terms = conn.execute("SELECT * FROM terms").fetchall()
    conn.close()
    return jsonify([dict(row) for row in terms])

# ✅ API: 단일 용어 조회
@app.route("/api/term/<title>", methods=["GET"])
def api_get_term(title):
    conn = get_db_connection()
    term = conn.execute("SELECT * FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return jsonify(dict(term))
    else:
        return jsonify({"error": "not found"}), 404

# ✅ API: 용어 추가
@app.route("/api/terms", methods=["POST"])
def api_add_term():
    data = request.get_json()
    title = data["title"]
    category = data["category"]
    content = data["content"]
    author = data["author"]
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO terms (title, category, content, author, last_editor, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, category, content, author, author, datetime.now())
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "added"}), 201

# ✅ API: 용어 수정
@app.route("/api/term/<title>", methods=["PUT"])
def api_edit_term(title):
    data = request.get_json()
    content = data["content"]
    editor = data["lastEditor"]
    conn = get_db_connection()
    conn.execute(
        "UPDATE terms SET content = ?, last_editor = ?, updated_at = ? WHERE title = ?",
        (content, editor, datetime.now(), title)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "updated"}), 200

# ✅ 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
