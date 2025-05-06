import sys
from crawler import AITimesCrawler
from db_manager import PostgresDBManager
from blog_writer import BlogWriter
import psycopg2
import os
from dotenv import load_dotenv

def get_all_companies_from_db():

    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename LIKE '%_articles';
    """)
    tables = cur.fetchall()
    cur.close()
    conn.close()

    return [t[0].replace("_articles", "").replace("_", " ").title() for t in tables]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ 실행 옵션이 필요합니다: crawl 또는 blog")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "crawl":
        crawler = AITimesCrawler()
        db = PostgresDBManager()

        df_all = crawler.crawl(max_pages=3)
        df_filtered = crawler.extract_articles_with_known_companies(df_all)
        df_final = crawler.add_article_content(df_filtered)

        for _, row in df_final.iterrows():
            for company in row["companies"].split(", "):
                db.insert_article_to_company_table(
                    company_name=company,
                    title=row["title"],
                    url=row["link"],
                    content=row["content"],
                    published_at=row["published_at"].replace(".", "-")
                )
        db.close()

    elif mode == "blog":
        if len(sys.argv) < 3:
            print("❗ blog 모드에서는 기업명을 최소 1개 이상 입력하거나 'all'을 입력하세요.")
            print("예시: python main.py blog OpenAI 네이버")
            print("예시: python main.py blog all")
            sys.exit(1)

        if sys.argv[2].lower() == "all":
            companies = get_all_companies_from_db()
        else:
            companies = sys.argv[2:]

        writer = BlogWriter()

        for company in companies:
            while True:
                print(f"🔎 {company} 사용하지 않은 기사 검색 중...")
                articles = writer.fetch_recent_articles(company)
                if len(articles) < 3:
                    print(f"⛔ {company} 기사 3개 미만 → 글 생성 종료\n")
                    break

                print(f"✍️ {company} 블로그 글 생성 중...")
                blog_text, used_ids, latest_date = writer.generate_blog_post(company, articles)
                filepath = writer.save_to_markdown(company, blog_text, latest_date)
                writer.mark_articles_as_used(company, used_ids)

                print(f"📄 블로그 생성 완료 → {filepath}\n")

        writer.close()

    else:
        print("❗ 지원하지 않는 모드입니다. 사용법: python main.py [crawl|blog 회사1 회사2 ...|blog all]")
