from openai import OpenAI
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import pathlib

class BlogWriter:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key = self.api_key)

        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.cur = self.conn.cursor()

    def _normalize_name(self, name):
        return name.lower().replace(" ", "_").replace("-", "_")

    def fetch_recent_articles(self, company_name, limit=3):
        table = self._normalize_name(company_name) + "_articles"
        self.cur.execute(f"""
            SELECT id, published_at, title, content FROM {table}
            WHERE used = FALSE
            ORDER BY published_at ASC
            LIMIT %s;
        """, (limit,))
        return self.cur.fetchall()

    def mark_articles_as_used(self, company_name, article_ids):
        table = self._normalize_name(company_name) + "_articles"
        self.cur.execute(f"""
            UPDATE {table}
            SET used = TRUE
            WHERE id = ANY(%s);
        """, (article_ids,))
        self.conn.commit()

    def generate_blog_post(self, company_name, articles):
        article_text = "\n\n".join([
            f"[{date}] {title}\n{content}" for _, date, title, content in articles
        ])
        prompt = f"""
        다음은 {company_name}에 대한 최근 뉴스 기사입니다. 이를 바탕으로, 사람들이 흥미롭게 읽을 수 있는 블로그 글을 작성해주세요.

        스타일은 다음과 같습니다:
        - ✅ 시선을 끌 수 있는 제목
        - ✍️ 친근하고 유쾌한 말투 (이모티콘 포함)
        - 🧩 각 이슈마다 소제목 사용 (`###`), 단 **기사 제목은 그대로 사용하지 말고 새롭게 표현**할 것
        - 🔥 자극적인 표현, 질문 등으로 독자 호기심 자극
        - 🖼️ 이미지 추천 위치는 "🖼️ 이미지: [설명]" 형식으로
        - 📝 마지막엔 간단한 요약 또는 마무리 인사

        아래는 기사 모음입니다:

        ### 기사 모음:
        {article_text}
        """

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 IT 전문 블로그 필자입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        blog = completion.choices[0].message.content
        usage = completion.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        cost = (prompt_tokens / 1000 * 0.03) + (completion_tokens / 1000 * 0.06)

        print(f"💰 [{company_name}] 토큰 사용량: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")
        print(f"💸 예상 비용: ${cost:.4f}\n")

        return blog, [row[0] for row in articles], articles[-1][1]  # blog text, used ids, latest date

    def save_to_markdown(self, company_name, blog_text, latest_date):
        print("⚙️ 파일 저장 중 ...")
        print(company_name, latest_date, blog_text[:20])
        
        folder = pathlib.Path("result") / self._normalize_name(company_name)
        folder.mkdir(parents=True, exist_ok=True)
        date_str = latest_date.strftime("%Y-%m-%d")
        filename = folder / f"{company_name}_{date_str}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(blog_text)
        print(f"✅ Markdown 저장 완료: {filename}")
        return filename

    def close(self):
        self.cur.close()
        self.conn.close()
        print("🔒 PostgreSQL 연결 종료")
