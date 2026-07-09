# Odds AI Pro V24 - No API BMBets

## 핵심
API 사용량이 없을 때 쓰는 버전입니다.

- The Odds API 사용 안 함
- API-SPORTS 사용 안 함
- BMBets HTML/JSON 파서만 사용
- 수집 실패 시 화면에 이유 표시
- 데모 fallback 유지

## Render 환경변수
```bash
ENABLE_BMBETS=1
ALLOW_DEMO_FALLBACK=1
MIN_START_MINUTES=10
MAX_START_MINUTES=720
```

## Render 설정
```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

## 중요한 한계
BMBets가 브라우저 JS로만 데이터를 그리면 Render의 requests 방식으로는 수집이 안 됩니다.  
그 경우 화면에 `파싱 실패: 사이트가 JS 렌더링이면 Render requests만으로 수집 불가`가 표시됩니다.

그때는 API가 아니라 Playwright 브라우저 수집 방식으로 바꿔야 합니다.


## V24 Fix
Render 오류 `ImportError: cannot import name 'BMBETS_URLS'` 수정 완료.
`collectors/config.py`에 BMBets 종목별 URL을 추가했습니다.
