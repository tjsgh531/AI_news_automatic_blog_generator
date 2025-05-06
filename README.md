# 📰 인공지능 뉴스 자동 요약 블로그 생성기

AI 관련 최신 뉴스를 자동으로 수집하고, 회사별로 정리해 마크다운 형식의 블로그 글을 생성하는 Python 프로젝트입니다.

# 📄 결과 예시
< 실제 생성한 블로그 이미지 >

<img width="800" alt="image" src="https://github.com/user-attachments/assets/3d5324be-8be1-452c-ba8a-a163ae9bbf5a" />


- 친근하고 이모지 포함된 블로그 스타일 뉴스 요약

- GPT 프롬프트와 토큰 사용량 및 비용 로그 출력

# 📁 프로젝트 구조
```
.
├── .env                    # 환경 변수 설정
├── main.py                 # 실행 스크립트
├── crawler.py              # AI Times 크롤러
├── db_manager.py           # PostgreSQL 데이터베이스 관리자
├── blog_writer.py          # 블로그 글 생성기 (GPT 활용)
├── craw_company_list.txt   # 기업명 리스트 (선택적 사용)
├── results/                # 생성된 마크다운 결과 저장 폴더
│   ├── openai/
│   ├── naver/
│   └── ...                 # 기업별 하위 폴더
└── requirements.txt        # 필요한 패키지 목록

```

# 🚀 실행 방법
### 1. 환경 변수 설정 (.env 파일):

```
OPENAI_API_KEY=your_openai_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### 2.의존성 설치
```
pip install -r requirements.txt
```

### 3. 뉴스 수집
```
python main.py crawl
```

### 4. 블로그 생성
```
# 특정 기업만 (기사 3개 이상일 때만 생성)
python main.py blog OpenAI 네이버

# 전체 기업 대상으로 반복적으로 작성 (기사 3개 이상일 때만 생성)
python main.py blog all
```

# 🧠 기능 요약

✅ AI Times 기반 뉴스 크롤링

✅ 회사 이름을 기준으로 필터링

✅ PostgreSQL에 회사별로 뉴스 저장

✅ 같은 뉴스 중복 저장 방지 (url 기준)

✅ 블로그 스타일의 글 자동 생성 (OpenAI GPT-4)

✅ 뉴스 사용 여부 관리 (used 필드)

✅ 기업별 마크다운 폴더 정리 및 저장
