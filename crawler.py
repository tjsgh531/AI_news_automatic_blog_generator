import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

AI_COMPANY_ALIASES = {
    "OpenAI": ["OpenAI", "오픈AI", "오픈에이아이"],
    "Google": ["Google", "구글"],
    "DeepMind": ["DeepMind", "딥마인드"],
    "Microsoft": ["Microsoft", "마이크로소프트", "MS"],
    "Amazon": ["Amazon", "아마존"],
    "Meta": ["Meta", "메타", "페이스북"],
    "NVIDIA": ["NVIDIA", "엔비디아"],
    "Anthropic": ["Anthropic", "앤트로픽"],
    "Mistral": ["Mistral", "미스트랄"],
    "xAI": ["xAI", "일론 머스크 AI", "일론머스크 AI"],
    "Cohere": ["Cohere", "코히어"],
    "Hugging Face": ["Hugging Face", "허깅페이스"],
    "Stability AI": ["Stability AI", "스테빌리티AI"],
    "네이버": ["네이버", "Naver", "하이퍼클로바"],
    "카카오": ["카카오", "Kakao"],
    "뤼튼": ["뤼튼", "Riiid", "Riiid!"],
    "업스테이지": ["업스테이지", "Upstage"],
    "티쓰리큐": ["T3Q", "티쓰리큐"],
    "솔트룩스": ["솔트룩스", "Saltlux"],
}

class AITimesCrawler:
    def __init__(self):
        self.results = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def crawl(self, max_pages=3):
        print("▶️ AI타임즈 기사 수집 시작...")
        for page in range(1, max_pages + 1):
            url = f"https://www.aitimes.com/news/articleList.html?page={page}&view_type=sm"
            print(f"📄 페이지 {page}: {url}")
            self.driver.get(url)
            time.sleep(2)

            try:
                ul = self.driver.find_element(By.CSS_SELECTOR, "ul.type2")
                li_list = ul.find_elements(By.TAG_NAME, "li")

                for li in li_list:
                    try:
                        title_tag = li.find_element(By.CSS_SELECTOR, "h4.titles > a")
                        title = title_tag.text.strip()
                        link = title_tag.get_attribute("href")

                        if link.startswith("/"):
                            link = "https://www.aitimes.com" + link

                        # ✅ 발행일 수집 (시간 제거)
                        byline = li.find_element(By.CLASS_NAME, "byline")
                        em_tags = byline.find_elements(By.TAG_NAME, "em")
                        full_date = em_tags[1].text.strip() if len(em_tags) > 1 else ""
                        published_date = full_date.split()[0] if full_date else ""

                        if title and link:
                            self.results.append({
                                "title": title,
                                "link": link,
                                "published_at": published_date
                            })
                    except:
                        continue
            except Exception as e:
                print("❌ 기사 목록 수집 실패:", e)

        self.driver.quit()
        return pd.DataFrame(self.results)

    def extract_articles_with_known_companies(self, df):
        print("🔍 기업명 필터링 중...")
        filtered = []
        
        for _, row in df.iterrows():
            title = row["title"]
            matched = []
            for company, aliases in AI_COMPANY_ALIASES.items():
                if any(alias in title for alias in aliases):
                    matched.append(company)
                    
            if matched:
                filtered.append({
                    "title": title,
                    "link": row["link"],
                    "published_at": row["published_at"],
                    "companies": ", ".join(set(matched))
                })
                
        return pd.DataFrame(filtered)

    def add_article_content(self, df):
        print("📝 기사 본문 수집 중...")
        contents = []
        for _, row in df.iterrows():
            content = self.get_article_content(row["link"])
            contents.append(content)
        df["content"] = contents
        return df

    def get_article_content(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, headers=headers, timeout=7)
            soup = BeautifulSoup(response.text, "lxml")

            body = soup.find("article", id="article-view-content-div")
            return body.get_text(strip=True) if body else ""
        except Exception as e:
            print(f"❌ 본문 수집 실패 ({url}): {e}")
            return ""
