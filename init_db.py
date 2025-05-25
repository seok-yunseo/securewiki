import sqlite3
from datetime import datetime

# DB 연결
conn = sqlite3.connect('wiki.db')
c = conn.cursor()

# 테이블 생성
c.execute('''
CREATE TABLE IF NOT EXISTS terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    author TEXT NOT NULL,
    last_editor TEXT,
    updated_at TEXT
)
''')

# 기본 용어 데이터
terms = [
    {
        "title": "ZeroDay",
        "content": "공개되기 전부터 존재하던 보안 취약점으로, 패치가 존재하지 않아 위험합니다.",
        "category": "system",
        "author": "admin",
    },
    {
        "title": "MITM",
        "content": "공격자가 통신 중간에 개입해 데이터를 가로채거나 조작하는 공격입니다.",
        "category": "network",
        "author": "admin",
    },
    {
        "title": "RCE",
        "content": "원격에서 악성 코드를 실행시킬 수 있는 취약점을 의미합니다.",
        "category": "system",
        "author": "admin",
    },
    {
        "title": "WAF",
        "content": "웹 애플리케이션 공격을 방지하는 방화벽 기술입니다.",
        "category": "web",
        "author": "admin",
    },
    {
        "title": "XSS",
        "content": "스크립트 삽입 공격",
        "category": "web",
        "author": "admin",
    },
    {
        "title": "CSRF",
        "content": "Cross Site Request Forgery",
        "category": "web",
        "author": "admin",
    },
    {
        "title": "SQLi",
        "content": "SQL 쿼리 조작 공격",
        "category": "web",
        "author": "admin",
    },
    {
        "title": "DDoS",
        "content": "분산 서비스 거부 공격",
        "category": "network",
        "author": "admin",
    },
    {
        "title": "PrivilegeEscalation",
        "content": "권한 상승 공격",
        "category": "system",
        "author": "admin",
    },
]

# 현재 시간
now = datetime.now().isoformat(timespec='seconds')

# 용어 삽입
for term in terms:
    try:
        c.execute('''
            INSERT OR IGNORE INTO terms (title, content, category, author, last_editor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (term['title'], term['content'], term['category'], term['author'], term['author'], now))
    except sqlite3.Error as e:
        print(f"❌ 삽입 오류: {term['title']} → {e}")

conn.commit()
conn.close()

print("✅ terms 테이블과 기본 용어들이 생성 및 삽입되었습니다.")
