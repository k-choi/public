# 배포 운영 가이드

이 저장소(`k-choi/public`)는 GitHub Pages로 공개되는 **정적 소설 사이트**입니다.
이 문서는 사이트가 어떻게 배포되고, 내용을 어떻게 갱신하는지 설명합니다.

- **라이브 주소:** https://k-choi.github.io/public/
- **배포 방식:** `main` 브랜치 푸시 → GitHub Actions → GitHub Pages (자동)

---

## 1. 저장소 구조

```
/
├── index.html              ← 서가(랜딩) 페이지. 두 작품으로 연결
├── README.md               ← 수록작 소개
├── DEPLOYMENT.md           ← 이 문서
├── .nojekyll               ← Jekyll 처리 비활성화(파일 그대로 서빙)
├── .github/workflows/
│   └── deploy-pages.yml     ← Pages 배포 워크플로
├── margin-of-error/        ← 「오차 범위」 (경로: /margin-of-error/)
│   ├── index.html           ← 리더(표지·차례·전 장, 라이트/다크)
│   ├── _full-novel.md       ← 전문 합본
│   └── manuscript/          ← 장별 원고(Markdown)
└── the-last-owner/         ← 「마지막 소유자」 (경로: /the-last-owner/)
    ├── index.html
    ├── _full-novel.md
    └── manuscript/
```

각 작품의 `index.html`은 **자체 완결형**입니다. CSS·스크립트·본문 텍스트가 한 파일에
모두 인라인되어 있어 외부 의존성이 없고, 링크는 모두 페이지 내 `#앵커`입니다.
따라서 파일 하나만 열어도 그대로 읽힙니다.

새 작품을 추가하려면 최상위에 **작품 전용 폴더**를 만들고(`/작품-슬러그/`),
그 안에 `index.html`을 두면 곧 `https://k-choi.github.io/public/작품-슬러그/`에서 열립니다.

---

## 2. 배포 원리

`.github/workflows/deploy-pages.yml`가 다음 경우에 실행됩니다.

- `main` 브랜치에 **푸시**할 때
- Actions 탭에서 **수동 실행**(`workflow_dispatch`)할 때

워크플로는 저장소 전체(`path: .`)를 Pages 아티팩트로 올려 배포합니다. 즉 **`main`에
올라간 파일이 곧 사이트**입니다. 별도 빌드 단계는 없습니다.

### 최초 1회 설정 (이미 완료됨)

GitHub 토큰만으로는 Pages를 처음 켤 수 없어, 저장소 소유자가 한 번 수동으로 활성화해야
합니다. 이미 완료되어 있으며, 혹시 다시 필요하면:

> **Settings → Pages → Build and deployment → Source = `GitHub Actions`**

---

## 3. 내용 갱신 방법

### 3-1. 원고/리더를 고칠 때

1. 해당 작품 폴더의 파일을 수정합니다.
   - 본문을 바꾸려면 `그-작품/index.html`(리더)과 `manuscript/`의 해당 장 파일을 함께 고칩니다.
     리더는 본문을 인라인으로 담으므로, **리더도 같이 갱신**해야 사이트에 반영됩니다.
2. 커밋 후 `main`에 푸시합니다.
   ```bash
   git add -A
   git commit -m "설명"
   git push origin main
   ```
3. 1~2분 뒤 자동 배포가 끝나면 라이브에 반영됩니다. (아래 4장으로 확인)

### 3-2. 소스 저장소에서 가져올 때 (권장 워크플로)

작품 원고의 정사(定史)는 소스 저장소 **`k-choi/NovelWriting`**에서 관리됩니다.

- 「오차 범위」: `NovelWriting`의 `public-site/`가 원저자 기준 최신 리더/원고입니다.
  기본 브랜치(`master`)가 전진하면 그 `public-site/`의 `index.html`·`_full-novel.md`·
  `manuscript/`를 이 저장소 `margin-of-error/`로 복사한 뒤 커밋·푸시합니다.
- 「마지막 소유자」: 정사 프로젝트는 `NovelWriting`의 `projects/the-last-owner/`에 있습니다.
  리더(`index.html`)는 `manuscript/chapter_*.md`로부터 생성합니다.

### 3-3. 「마지막 소유자」 리더 재생성

리더는 장별 Markdown에서 생성된 자체 완결형 HTML입니다. 원고가 바뀌면 같은 디자인으로
다시 만들어 교체합니다. (생성 스크립트가 필요하면 요청 시 이 저장소에 함께 보관합니다.)

---

## 4. 배포 확인

```bash
# 사이트가 살아 있는지 (200이면 정상)
curl -s -o /dev/null -w '%{http_code}\n' https://k-choi.github.io/public/
curl -s -o /dev/null -w '%{http_code}\n' https://k-choi.github.io/public/margin-of-error/
curl -s -o /dev/null -w '%{http_code}\n' https://k-choi.github.io/public/the-last-owner/
```

- 워크플로 상태는 저장소 **Actions** 탭의 "Deploy Pages" 실행에서 확인합니다.
- 방금 올린 내용이 반영됐는지는 로컬 파일과 라이브 응답을 비교하면 확실합니다.
  ```bash
  # 예: 리더가 방금 배포본과 동일한지 md5로 대조
  L=$(md5sum margin-of-error/index.html | cut -d' ' -f1)
  curl -s https://k-choi.github.io/public/margin-of-error/ | md5sum
  echo "local: $L"
  ```
- CDN 캐시 때문에 갱신 반영이 30초~1분 늦을 수 있습니다. 잠시 뒤 다시 확인하세요.

---

## 5. 자주 겪는 상황

| 증상 | 원인 / 해결 |
|------|-------------|
| 푸시했는데 안 바뀜 | 배포 지연 또는 CDN 캐시. 1분 뒤 재확인. Actions에서 실행 성공 여부 확인. |
| 워크플로 첫 실행 실패(`Create Pages site failed`) | Pages가 아직 안 켜짐 → Settings → Pages → Source를 `GitHub Actions`로 지정 후 재실행. |
| 리더는 그대로인데 `manuscript/`만 고침 | 리더(`index.html`)는 본문을 인라인으로 담으므로 **리더도 같이 갱신**해야 함. |
| 특정 작품만 404 | 해당 `작품-슬러그/index.html`이 있는지, 경로 철자가 맞는지 확인. |

---

## 6. 요약

- **`main`에 올린 파일 = 라이브 사이트.** 빌드 없음.
- 작품마다 **자체 완결형 `index.html`** 하나로 읽힘.
- 원고 정사는 `k-choi/NovelWriting`, 공개본은 이 저장소.
- 갱신은 **파일 수정 → `main` 푸시 → 자동 배포 → 확인** 순서.
