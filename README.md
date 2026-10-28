# cookDB 첫 웹 앱 — 학생용 시작 프로젝트

## 준비
- MySQL Server와 Workbench에서 `cookDB.sql`을 실행하여 `cookDB`를 생성합니다.
- VS Code, Python 3.12, VS Code Python 확장을 설치합니다.

## 실행 (Windows PowerShell)
프로젝트 폴더에서:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`.streamlit/secrets.example.toml`을 **같은 폴더의** `secrets.toml`로 복사하고 내 MySQL 계정과 비밀번호를 입력합니다.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 실행 (macOS)
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m streamlit run app.py
```

브라우저에서 터미널에 표시된 `http://localhost:8501` 주소를 엽니다.

## 데이터 검증 기준
- `userTBL`: 10행
- `buyTBL`: 12행
- 구매 회원: 5명
- 전체 구매금액 데이터 합계(`SUM(price*amount)`): 3500

> 원본 `buyTBL`에는 **구매일자**가 없습니다. 따라서 일별/월별 매출 기능은 이번 실습에서 만들지 않습니다.

> `.streamlit/secrets.toml`은 개인 비밀번호가 들어 있으므로 공유하거나 제출하지 않습니다.
