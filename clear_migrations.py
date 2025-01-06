import sqlite3

# 데이터베이스 파일 경로 설정
db_path = 'db.sqlite3'

# SQLite 데이터베이스 연결
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# django_migrations 테이블의 모든 레코드 삭제
cur.execute("DELETE FROM django_migrations")

# 변경 사항 커밋 및 연결 닫기
conn.commit()
conn.close()

print("Migration history cleared.")