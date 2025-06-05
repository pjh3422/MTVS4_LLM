# 버디 봇 (Memorization System)

**“장기기억 봇” 프로젝트는 사용자가 암기 카드를 생성하고, 단계별 복습 알고리즘을 통해 장기 기억에 효과적으로 저장할 수 있도록 돕는 학습 도구입니다.**

- **프로젝트 기간:** 2025.05.19 ~ 2025.06.05  
- **팀원 구성:**  
  - 박정호, 박민주, 신재성, 최유성

---

## 1. 주요 기능

1. **카드 생성 & 관리**  
   - 개념(concept) 또는 단어(word) 형식의 암기 카드 생성  
   - 백엔드 SQLite 데이터베이스에 카드 정보 저장  
   - 카드 수정, 삭제, 전체 목록 조회 기능 제공

2. **단계별 복습 & 알림**  
   - **스페이싱 효과** 기반 복습 일정  
     - 1단계: 즉시 복습  
     - 2단계: 10분 뒤  
     - 3단계: 24시간 뒤  
     - 4단계: 일주일 뒤  
     - 5단계 이상: 한 달 뒤  
   - 복습이 필요한 카드를 조회하여 복습 화면에 표시  
   - 테스트 모드 활성화 시 즉시 모든 카드를 복습 가능

3. **힌트 제공**  
   - 카드 타입(word/concept)과 현재 단계(stage)에 따라 서로 다른 힌트 노출  
     - **word**  
       - 1단계: 힌트 없음 (바로 정답 입력)  
       - 2단계: 간단 마스킹 힌트 (첫 글자 + “*” 형태)  
       - 3단계: LLM을 활용한 짧은 힌트 (정답 노출 금지, 1문장 이내)  
       - 4단계: LLM을 활용한 구체 힌트 (정답 노출 금지, 최대 2문장 이내)  
     - **concept**  
       - 1단계: 힌트 없음  
       - 2단계: LLM을 활용한 짧은 힌트 (정의 노출 금지, 1문장 이내)  
       - 3단계: LLM을 활용한 짧은 힌트 (정의 노출 금지, 1문장 이내)  
       - 4단계: LLM을 활용한 구체 힌트 (정의 노출 금지, 최대 2문장 이내)  

4. **피드백 & 재시도 로직**  
   - 사용자가 정답 입력 시 LLM이 문장 의미 유사도를 계산해 채점  
   - 정답일 경우 간단한 칭찬 피드백 제공  
   - 오답일 경우 사용자 답변을 바탕으로 학습자가 스스로 떠올릴 수 있도록 유도하는 힌트 피드백 제공  
   - **재시도 로직**  
     - 첫 오답 시 즉시 재시험 기회 1회 부여  
     - 재시험 기회 소진 후 오답일 경우 단계 초기화(1단계 → 10분 뒤 복습)  
     - 일반 모드: 재시험 대기 30초 (타이머 노출)  
     - 테스트 모드: 재시험 대기 5초

5. **심화 문제 & 연관 개념 추천**  
   - 4단계까지 통과한 카드에 대해 LLM이 자동으로 심화 문제(n개) 생성  
   - 연관 개념 리스트를 LLM으로 추천 → 프론트엔드 모달로 사용자 선택  
   - 사용자가 선택한 연관 개념을 바로 “개념 카드”로 자동 생성 후 정의 표시

---

## 2. 사전 준비

1. **Node.js 설치**  
   - [Node.js 공식 사이트](https://nodejs.org/)에서 최신 LTS 버전 다운로드 & 설치

2. **Ollama 설치**
   - [Ollama 공식 사이트](https://ollama.com/download)에서 Ollama 설치 및 터미널에서 ollama pull gemma3:4b-it-qat 실행(최초 1회)

4. **VSCode 익스텐션**  
   - PostCSS Language Support  
   - Tailwind CSS IntelliSense  
   - SQLite (SQLite Viewer 등)

5. **Python 환경**  
   - Python 3.12 이상 (가상환경 권장)  
   - `uvicorn`, `fastapi`, `pydantic`, `langchain-ollama`, `sentence-transformers` 등

6. **Git (선택 사항)**  
   - 프로젝트 버전 관리를 위해 Git 설치 및 GitHub 계정 준비

---

## 3. 프로젝트 구조
```
memorization_system/
├── backend/
│ ├── api.py
│ ├── services/
│ │ ├── card_service.py
│ │ ├── review_service.py
│ │ ├── schedule_service.py
│ │ └── llm_service.py
│ ├── storage/
│ │ └── sqlite_storage.py
│ ├── models/
│ │ ├── card.py
│ │ └── review.py
│ ├── interfaces/
│ │ └── llm_interface.py
│ ├── config/
│ │ └── settings.py
│ ├── requirements.txt
│ └── cards.db # SQLite DB (Git에 포함하지 않음)
│
└── frontend/
├── public/
│ └── index.html
├── src/
│ ├── components/
│ │ ├── ReviewPage.jsx
│ │ └── RelatedConceptModal.jsx
│ ├── services/
│ │ └── api.js
│ ├── App.jsx
│ ├── index.jsx
│ └── index.css
├── package.json
├── package-lock.json
└── tailwind.config.js
```

- **backend/**: FastAPI 서버 코드, 서비스 로직, SQLite 스토리지, LLM 연동  
- **frontend/**: React + Tailwind CSS 기반 UI, 복습 페이지, 모달 컴포넌트, API 호출 모듈  

---

## 4. 실행 방법

### 4.1 백엔드 서버

1. 터미널에서 프로젝트 폴더로 이동  
   ```bash
   cd memorization_system/backend

2. (최초 1회) Python 가상환경 생성 및 활성화
    ```bash
    conda craete -v 가상환경이름 python=3.12

3. 의존성 패키지 설치
    ```bash
    pip install -r requirements.txt

4. 서버 실행
    ```bash
    python api.py

- 기본적으로 http://0.0.0.0:8000에서 FastAPI 서버가 실행됩니다.
- `reload=True` 옵션 덕분에 코드 수정 시 자동 리로드됩니다.

### 4.2 프론트엔드 애플리케이션

1. 다른 터미널 창/탭을 열어 프론트엔드 폴더로 이동
    
    ```bash
    cd memorization_system/frontend
    
    ```
    
2. (최초 1회) 패키지 설치
    
    ```bash
    npm install
    
    ```
    
3. 개발 서버 실행
    
    ```bash
    npm start
    
    ```
    
    - 기본적으로 `http://localhost:3000`에서 React 개발 서버가 실행됩니다.
    - 브라우저가 자동으로 열리며, UI를 통해 복습 기능을 체험할 수 있습니다.
---

# 

## 5. 주요 라이브러리 & 버전

### 5.1 백엔드

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- langchain-ollama
- sentence-transformers
- scikit-learn (cosine_similarity)
- SQLite (sqlite3)

### 5.2 프론트엔드

- Node.js 20.x 이상
- React 18.x
- Tailwind CSS 3.x
- Framer Motion
- Axios

---

## 6. 주요 화면 & 흐름

1. **메인 대시보드**
    - “복습하기” 버튼을 눌러 복습 페이지로 이동
    - 테스트 모드 토글을 통해 즉시 복습 / 일반 복습 전환 가능
2. **복습 페이지 (ReviewPage.jsx)**
    - 복습이 필요한 카드 목록(문제 텍스트) 표시
    - 단계별 힌트: 1단계는 힌트 없음, 이후 단계부터 힌트 노출
    - 답안 입력 후 “제출” 버튼 클릭
    - 정답 시 → 간단 알림 후 다음 카드 로드
    - 오답 시 → 재시도 로직 (30초/5초 대기, 타이머 표시)
    - 4단계 정답 시 → 관련 개념 모달로 연관 개념 선택 → 새로운 개념 카드 생성
3. **관련 개념 생성 모달 (RelatedConceptModal.jsx)**
    - LLM이 추천한 연관 개념 리스트를 한눈에 보여줌
    - 사용자가 선택한 개념은 즉시 “개념 카드”로 자동 생성되고, 생성된 정의를 알림창에 표시

---

## 7. Git 관리 & 주의 사항

1. **`.gitignore` 예시**
    
    ```gitignore
    # Python 가상환경
    .venv/
    __pycache__/
    *.pyc
    
    # SQLite DB 파일
    cards.db
    *.db
    
    # Node.js
    node_modules/
    
    # VSCode 설정
    .vscode/
    
    ```
    
    - `cards.db` 파일은 Git에 포함하지 않고, 로컬에서 자동 생성되도록 합니다.
    - `node_modules/` 역시 커밋하지 않습니다.

---

## 8. 추가 참고 자료

- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **Tailwind CSS 공식 문서**: https://tailwindcss.com/
- **Framer Motion 가이드**: https://www.framer.com/motion/
- **langchain-ollama**: https://github.com/jina-ai/langchain-ollama
- **sentence-transformers**: https://www.sbert.net/
- **SQLite 튜토리얼**: https://www.sqlite.org/index.html

--- 
