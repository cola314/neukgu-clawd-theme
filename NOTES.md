# 늑구 (Neukgu) 테마 작업 노트

> Clawd on Desk용 카툰 늑대 데스크펫 테마. Nano Banana (Gemini 2.5 Flash Image via OpenRouter)로 AI 생성.

---

## 📊 최종 진도 (2026-04-22)

| 구분 | 상태 | 프레임 | 비고 |
|------|------|-------|------|
| idle (eye tracking) | ✅ 하이브리드 SVG (PNG + 오버레이) | - | body-js / eyes-js / shadow-js 그룹 |
| working/typing | ✅ 3프레임 루프 | 3 | 앉아 키보드 타이핑 |
| thinking | ✅ 3프레임 루프 | 3 | 꼬리+귀 애니 + 흰 "?" |
| attention/happy | ✅ 3프레임 루프 | 3 | Cheer wave + 노란 스파클 |
| notification | ✅ 3프레임 루프 | 3 | 귀 쫑긋 + 흰 "!" |
| error | ✅ 3프레임 루프 | 3 | >< 눈 + 흰 "!?" + 머리 흔들 |
| sleeping | ✅ 3프레임 루프 | 3 | 누워서 호흡 + 흰 "Zzz" |

**MVP 7개 완성 ✅**

**누적 비용**: ~$1.32 (약 1,850원)

---

## 🎯 목표

**25개 상태 × 평균 3~5 프레임 APNG 테마**를 AI 이미지 생성으로 만든다. 첫 MVP는 개별 상태로 나누어 점진적 완성.

---

## 🐺 캐릭터 & 레퍼런스

- **이름**: 늑구 (Neukgu)
- **원본 레퍼런스**: `themes/neukgu/assets/idle.png` — ChatGPT(OpenAI DALL-E)로 생성한 카툰 늑대 PNG (사용자 제공)
- **스타일**: 카툰 벡터, 볼드 검은 아웃라인, 탠/베이지 털 + 크림색 가슴, 볼 tuft, 프로미넌트한 꼬리
- **뷰**: 원본 idle는 측면 3/4 서있는 자세. 나머지 상태는 typing-f1 기반 3/4 앉은 자세 (앵커로 사용). sleeping은 예외 — 누운 자세.

---

## 🏗️ 환경 & 선택

| 항목 | 결정 | 근거 |
|------|------|------|
| GPU | NVIDIA RTX 1000 Ada Laptop, 6GB VRAM | - |
| 로컬 생성 | 포기 | 6GB로는 Flux 풀/Z-Image 못 돌림 |
| 클라우드 모델 | **Nano Banana** (Gemini 2.5 Flash Image) via OpenRouter | 캐릭터 일관성 + multi-turn 편집 최강, $0.04/이미지 |

---

## 📂 파이프라인 구조

```
themes/neukgu/
├── theme.json                 # 테마 메타 (7개 상태 + eye tracking)
├── preview.html               # 브라우저 비교 뷰어
├── NOTES.md                   # 이 파일
└── assets/
    ├── idle.png               # 원본 레퍼런스 (ChatGPT 제작)
    ├── idle-eyeless.png       # 눈 지운 버전 (SVG 오버레이용)
    ├── idle-follow.svg        # 하이브리드 SVG (eye tracking)
    ├── typing.apng            # working 루프
    ├── thinking.apng          # thinking 루프
    ├── happy.apng             # attention 루프 (노란 스파클)
    ├── notification.apng      # 흰 "!" 알림 루프
    ├── error.apng             # 흰 "!?" 에러 루프
    ├── sleeping.apng          # 흰 "Zzz" 수면 루프
    ├── *-f1/2/3.png           # 상태별 프레임 (align 전)
    ├── *-v1.png / *-v2.png    # 구 버전 백업
    └── aligned/               # 정렬된 프레임 (중간물)

scripts/neukgu/
├── gen-frame.py               # OpenRouter 호출 (--confirm 없으면 dry-run)
├── transparent-bg.py          # 투명 배경 변환 (흰 bg / 검정 bg / 투명 bg 모두 지원)
├── align-frames.py            # 프레임 정렬 (bbox + ROI + x/y-anchor)
├── assemble-apng.py           # PNG → APNG 합성
├── find-eyes.py               # PNG 눈 좌표 자동 검출
├── erase-eyes.py              # PNG 눈 지우기 (eye tracking 배경용)
├── recolor-symbol.py          # 특정 영역 다크 클러스터 재채색 (실험용 — 최종 미사용)
├── check-alpha.py, check-pixel.py, check-svg.py  # 디버깅
└── prompts/
    ├── typing-f1/2/3.txt
    ├── thinking-f1/2/3.txt
    ├── happy-f1/2/3.txt
    ├── notification-f1/2/3.txt
    ├── error-f1/2/3.txt
    └── sleeping-f1/2/3.txt
```

---

## 🔧 파이프라인 표준 순서 (상태 추가 시)

```
1. 프롬프트 작성
   - F1: 큰 포즈 + 심볼 색상 명시 ("WHITE INTERIOR + BLACK OUTLINE")
   - F2/F3: delta만 (어느 부분이 움직이는지 명시)
2. gen-frame.py로 F1 생성 (사용자 승인 후 --confirm)
3. 결과 OK면 F2, F3 병렬 생성 (F1을 reference anchor로)
4. transparent-bg.py --mode border (흰/검정/투명 모두 자동 감지)
5. align-frames.py (보통 --x-anchor right/center --y-anchor bottom, 포즈 변형 큰 경우 --roi)
6. assemble-apng.py --duration 180~400
7. theme.json states에 추가
8. userData로 배포 (+ SVG 참조 PNG는 theme-cache로도 복사)
9. preview.html 업데이트
```

---

## 💡 핵심 교훈 (메모리 저장됨)

### 1. API 호출 승인 프로토콜
1 프레임이라도 허락 없이 호출 금지. `gen-frame.py`는 `--confirm` 없으면 dry-run.

### 2. Freeze는 정밀하게, 전역 금지
- ❌ "FREEZE everything" (모델 혼란)
- ✅ "MUST STAY IDENTICAL: face, body" + "CHANGE: tail, ears" (구체적 리스트)

### 3. F1 앵커링 vs 체이닝
F2/F3 모두 F1을 레퍼런스로 (체인 X). 드리프트 누적 방지.

### 4. Bbox 정렬은 필수 후처리
Nano Banana 프레임마다 sub-pixel 단위 wobble. `align-frames.py` 필수.
- 옵션: `--x-anchor left/center/right`, `--y-anchor top/center/bottom`, `--roi x0,y0,x1,y1`
- 포즈 변형 큰 상태(팔 올리기/기울이기/누움)는 반드시 **ROI 기반 정렬 (몸통 코어만 기준)**

### 5. 투명 배경 처리 (transparent-bg.py)
Nano Banana 출력 종류:
- **흰색 배경 opaque** → border flood-fill로 투명화
- **검정 배경 opaque** (간혹 발생) → dark-border flood-fill 필요 (구현됨)
- **이미 투명 RGBA** → 건드리지 말고 passthrough (구현됨)

### 6. 정렬 시 RGBA 투명 fill
Shift로 노출된 가장자리를 **`(0, 0, 0, 0)` 투명 흰색**으로 채워야 함. 불투명 흰색이면 strip 자국.

### 7. ROI 정렬
꼬리/팔/심볼 움직임이 bbox 양끝을 흔드는 경우, **몸통 코어 영역**만 bbox 계산 기준 삼기.
- happy: ROI 250,500,700,870 (팔 위쪽 + 꼬리 오른쪽 제외)
- notification/error/sleeping: ROI 200,500,700,870 (몸통 하부)

### 8. Eye Tracking 하이브리드 (PNG + SVG overlay)
**구조**:
```
<svg viewBox="0 0 200 200">
  <g id="shadow-js">  <!-- 바닥 타원 그림자 --> </g>
  <g id="body-js">    <!-- 눈 지운 PNG 임베드 --> </g>
  <g id="eyes-js">    <!-- 오버레이 눈 2개 (translate로 이동) --> </g>
</svg>
```
**핵심 트릭**: `erase-eyes.py`로 PNG 원본 눈을 fur color로 메우고, SVG에 오버레이 눈을 얹는다. 오버레이가 어디로 이동해도 원본 눈 노출 없음.

**튜닝 값 (최종)**:
- `maxOffset: 2.0` (viewBox 200 기준 1%)
- `bodyScale: 0.2` (몸은 눈의 20%)
- 오버레이 ellipse rx=2.15, ry=2.9 (80% scale 기준)

### 9. Clawd 외부 테마 SVG 이슈 (중요!)
- **XML 선언 제거**: `<?xml ... ?>` 있으면 Clawd sanitizer가 `?>`를 잘라먹어 파싱 실패. `<svg>`부터 시작할 것.
- **상대 href PNG 참조**: 외부 테마의 SVG만 `theme-cache/`로 복사되고 PNG는 원본 dir에 남아 상대경로 깨짐.
  - 해결: 설치 스크립트가 참조 PNG도 cache에 수동 복사 (`install.ps1` / `install.sh`)
- **캐시 강제 재빌드**: `rm {userData}/theme-cache/<id>/assets/<file>.svg` 후 재로드

### 10. 심볼 색상 (흰색 심볼 전략) — 결정적 교훈
**후처리 recolor는 근본적으로 불안정**. connected-components가 심볼과 wolf 부위 100% 구분 못 함.

**대신 프롬프트에서 직접 요청**:
```
"A SINGLE '!' symbol drawn with SOLID WHITE INTERIOR FILL and a thin BLACK OUTLINE"
```
Nano Banana가 처음부터 "흰 속 + 검은 외곽"으로 그린다. 후처리 필요 없음. 안정적.

### 11. 로컬 fileScales 이슈
theme.json의 `objectScale.fileScales`는 초기 렌더 시 적용 안 됨 (첫 프레임만 풀사이즈로 뜸).
**대안**: SVG 자체에서 `<image x="20" y="20" width="160" height="160">` 같이 하드코딩으로 스케일. 눈 좌표도 스케일에 맞춰 계산.

---

## ⚠️ Clawd 테마 시스템 필수사항

- `schemaVersion: 1`, `name`, `version` 필수
- **REQUIRED_STATES**: `idle`, `working`, `thinking`, `sleeping`, `waking` — 다 있어야 테마 로드됨 (없으면 fallback으로 다른 상태 가리키기)
- **sleepSequence.mode**: `full`이면 yawning/dozing/collapsing 필수, `direct`면 생략 가능
- **viewBox**: SVG 단위 로직 캔버스. 애셋의 aspect ratio와 맞춰야 함
- **hitBoxes.default** 필수
- Asset 경로는 assets/ 기준 파일명만

---

## 🎨 최종 theme.json 구조

```json
{
  "schemaVersion": 1,
  "viewBox": { "x": 0, "y": 0, "width": 200, "height": 200 },
  "eyeTracking": {
    "enabled": true,
    "states": ["idle"],
    "maxOffset": 2.0,
    "bodyScale": 0.2,
    "ids": { "eyes": "eyes-js", "body": "body-js", "shadow": "shadow-js" }
  },
  "states": {
    "idle":         ["idle-follow.svg"],
    "working":      ["typing.apng"],
    "thinking":     ["thinking.apng"],
    "attention":    ["happy.apng"],
    "notification": ["notification.apng"],
    "error":        ["error.apng"],
    "sleeping":     ["sleeping.apng"],
    "waking":       ["idle.png"]
  },
  "sleepSequence": { "mode": "direct" },
  "hitBoxes": { "default": { "x": 30, "y": 30, "w": 140, "h": 150 } },
  "miniMode": { "supported": false },
  "objectScale": { "widthRatio": 0.7, "heightRatio": 0.7 }
}
```

---

## 🔑 API 키 보안

- OpenRouter 키는 세션 환경변수로만 사용 (`OPENROUTER_API_KEY`)
- 파일/스크립트/.env/git에 절대 저장 안 함
- 프로젝트 종료 후 rotate 권장

---

## 🚀 향후 확장 방향

1. **Tier 2 sleep 시퀀스**: yawning / dozing / collapsing / waking (현재는 `direct` 모드로 skip)
2. **Tier 3 working 변형**: juggling (2세션) / building (3+세션) / conducting (subagent) / sweeping / carrying
3. **Tier 4 리액션**: drag / click-left / click-right / double-click
4. **Tier 5 Mini Mode**: 7종 (현재 비활성화)
5. **Clawd 업스트림 PR**: SVG sanitizer XML 선언 보존 + 비-SVG 자산 캐시 복사

---

## 📦 배포: GitHub 레포

별도 레포 `cola314/neukgu-clawd-theme`에 최종 산출물 공개. `install.ps1` / `install.sh` 포함해 원커맨드 설치 지원.
