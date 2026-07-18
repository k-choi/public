# 서가

한국어 장편소설 두 편을 온라인으로 읽을 수 있는 정적 사이트입니다.

**https://k-choi.github.io/public/**

## 수록작

| # | 작품 | 장르 | 분량 | 경로 |
|---|------|------|------|------|
| 01 | **오차 범위** | 현대 로맨스 스릴러 | 전 4부 28장 | [`/margin-of-error/`](https://k-choi.github.io/public/margin-of-error/) |
| 02 | **마지막 소유자** | 사변적 가족소설 · 심리 서스펜스 | 전 30장 | [`/the-last-owner/`](https://k-choi.github.io/public/the-last-owner/) |

각 작품 폴더 구성:

- `index.html` — 리더(표지·차례·전 장, 라이트/다크)
- `manuscript/` — 장별 원고(Markdown)
- `_full-novel.md` — 전문 합본

루트 `index.html`은 두 작품으로 이어지는 서가(랜딩) 페이지입니다.

## 배포

`.github/workflows/deploy-pages.yml`가 `main` 푸시 시 GitHub Pages로 자동 배포합니다.
자동 활성화가 막히면 저장소 Settings → Pages → Source를 **GitHub Actions**로 한 번만 지정하세요.
