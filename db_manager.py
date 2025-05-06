import os
import psycopg2
from dotenv import load_dotenv

class PostgresDBManager:
    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.cur = self.conn.cursor()
        print("✅ PostgreSQL 연결 성공")

    def _normalize_name(self, name):
        return name.lower().replace(" ", "_").replace("-", "_")

    def create_company_table(self, company_name):
        table_name = self._normalize_name(company_name) + "_articles"
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                title TEXT,
                url TEXT UNIQUE,
                content TEXT,
                published_at DATE,
                used BOOLEAN DEFAULT FALSE
            );
        """)
        self.conn.commit()
        return table_name

    def insert_article_to_company_table(self, company_name, title, url, content, published_at):
        table_name = self.create_company_table(company_name)
        try:
            self.cur.execute(f"""
                INSERT INTO {table_name} (title, url, content, published_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
            """, (title, url, content, published_at))
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(f"✅ [{company_name}] 저장됨: {title}")
                return True
            else:
                print(f"⚠️ [{company_name}] 중복으로 저장 안됨: {title}")
                return False

        except Exception as e:
            print(f"❌ [{company_name}] 삽입 오류:", e)
            self.conn.rollback()
            return False

    def close(self):
        self.cur.close()
        self.conn.close()
        print("🔒 PostgreSQL 연결 종료")
