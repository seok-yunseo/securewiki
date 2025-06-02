# Flask 웹 프레임워크 및 필요한 라이브러리 가져오기
from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

import init_db # DB 초기화 모듈 (초기 스키마를 생성하는 용도)

app = Flask(__name__)

# ✅ SQLite DB에 연결하는 함수
def get_db_connection():
    conn = sqlite3.connect('wiki.db') # wiki.db 파일에 연결
    conn.row_factory = sqlite3.Row # 딕셔너리처럼 컬럼명으로 접근 가능하게 설정
    return conn

# ✅ 메인 페이지 (검색 기능 포함)
@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('q', '') # 검색어를 URL에서 가져옴 (?q=키워드)
    conn = get_db_connection()
    if keyword:
        # 검색어가 있을 경우: 제목 또는 내용에서 검색어 포함된 항목만 조회
        query = "SELECT * FROM terms WHERE title LIKE ? OR content LIKE ?"
        terms = conn.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()
    else:
         # 검색어가 없을 경우: 전체 용어 조회
        terms = conn.execute("SELECT * FROM terms").fetchall()
    conn.close()
    return render_template('index.html', terms=terms, keyword=keyword) # 템플릿에 데이터 전달

# ✅ 특정 용어 보기
@app.route('/term/<title>', methods=['GET'])
def view_term(title):
    conn = get_db_connection()
    term = conn.execute("SELECT * FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return render_template('view_term.html', term=term) # 해당 용어 페이지로 이동
    else:
        return f"❌ '{title}' 용어가 존재하지 않습니다.", 404 # 존재하지 않을 경우 404 에러

# ✅ 용어 추가 페이지 및 처리
@app.route('/add', methods=['GET', 'POST'])
def add_term():
    if request.method == 'POST':
        # 폼에서 입력된 데이터 수집
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        editor = request.form['editor']
        # DB에 새 용어 삽입
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO terms (title, content, category, author, last_editor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, category, editor, editor, datetime.now()))
        conn.commit()
        conn.close()
        # 새로 추가한 용어 페이지로 리디렉션
        return redirect(url_for('view_term', title=title))  # 등록 후 상세 페이지로 이동
    return render_template('add_term.html') # GET 요청이면 입력 폼 보여주기


# ✅ 용어 수정 페이지 및 처리
@app.route('/edit/<title>', methods=['GET', 'POST'])
def edit_term(title):
    conn = get_db_connection()
    if request.method == 'POST':
        # 수정된 내용 처리
        new_content = request.form['new_content']
        editor = request.form.get('editor', 'unknown') # 작성자 이름 기본값 설정
        conn.execute('''
            UPDATE terms
            SET content = ?, last_editor = ?, updated_at = ?
            WHERE title = ?
        ''', (new_content, editor, datetime.now(), title))
        conn.commit()
        conn.close()
        return redirect(url_for('view_term', title=title)) # 수정 후 상세 페이지로 이동
    # 수정 폼을 위한 기존 내용 불러오기
    term = conn.execute("SELECT content FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return render_template('edit_term.html', title=title, content=term['content'])
    else:
        return f"❌ '{title}' 용어가 존재하지 않습니다.", 404

# ✅ REST API: 전체 용어 목록 조회 (JSON 형식)
@app.route("/api/terms", methods=["GET"])
def api_get_terms():
    conn = get_db_connection()
    terms = conn.execute("SELECT * FROM terms").fetchall()
    conn.close()
    return jsonify([dict(row) for row in terms]) # Row 객체를 dict로 변환해서 JSON 반환


# ✅ REST API: 특정 용어 조회
@app.route("/api/term/<title>", methods=["GET"])
def api_get_term(title):
    conn = get_db_connection()
    term = conn.execute("SELECT * FROM terms WHERE title = ?", (title,)).fetchone()
    conn.close()
    if term:
        return jsonify(dict(term)) # JSON으로 해당 용어 리턴
    else:
        return jsonify({"error": "not found"}), 404 # 에러 처리

# ✅ REST API: 용어 추가
@app.route("/api/terms", methods=["POST"])
def api_add_term():
    data = request.get_json() # JSON 데이터 받기
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
    return jsonify({"message": "added"}), 201 # 201: 생성 성공 응답

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
    return jsonify({"message": "updated"}), 200 # 200: 성공 응답

# ✅ 서버 실행 (호스팅 환경에서도 동작하도록 포트 지정)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) # 환경 변수로부터 포트 가져오거나 기본값 5000 사용
    app.run(host='0.0.0.0', port=port) # 외부 접속 허용 (개발 서버)

