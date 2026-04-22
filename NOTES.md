# 늑구 (Neukgu) 테마 작업 노트

> Clawd on Desk용 카툰 늑대 데스크펫 테마. Nano Banana (Gemini 2.5 Flash Image via OpenRouter)로 AI 생성.

---

## 📊 현재 진도 (2026-04-21 기준)

| 구분 | 상태 | 프레임 | 비용 |
|------|------|-------|------|
| idle (eye tracking) | ✅ SVG 하이브리드 (idle-eyeless.png + overlay) | — | $0 |
| working/typing | ✅ 3프레임 루프 | 3 | $0.20 |
| thinking | ✅ 3프레임 루프 (꼬리+귀 애니, "?" 심볼) | 3 | $0.12 |
| attention/happy | ✅ 3프레임 루프 (cheer wave, 노란 스파클) | 3 | $0.20 |
| notification | ⏳ 미완 | - | - |
| error | ⏳ 미완 | - | - |
| sleeping | ⏳ 미완 (idle 폴백) | - | - |
| **누적 비용** | — | — | **$0.52** (≈ 735원) |

MVP 7개 중 **4개 완성 + eye tracking 구현 완료**. 나머지 3개 MVP 상태 남음.

---

## 🎯 목표

**25개 상태 × 평균 3~5 프레임 APNG 테마**를 AI 이미지 생성으로 만든다. 첫 MVP는 개별 상태로 나누어 점진적 완성.

---

## 🐺 캐릭터 & 레퍼런스

- **이름**: 늑구 (Neukgu)
- **원본 레퍼런스**: `themes/neukgu/assets/idle.png` — 사용자가 다운로드한 카툰 늑대 PNG
- **스타일**: 카툰 벡터, 볼드 검은 아웃라인, 탠/베이지 털 + 크림색 가슴, 볼 tuft, 프로미넌트한 꼬리
- **뷰**: 3/4 앉은 자세 (typing-f1 기준, 이후 anchor로 사용)

---

## 🏗️ 환경 & 선택

| 항목 | 결정 | 근거 |
|------|------|------|
| GPU | NVIDIA RTX 1000 Ada Laptop, **6GB VRAM** | — |
| 로컬 생성 | 포기 | 6GB로는 Flux 풀/Z-Image 못 돌림 |
| 클라우드 모델 | **Nano Banana** (Gemini 2.5 Flash Image) via **OpenRouter** | 캐릭터 일관성 + multi-turn 편집 최강, $0.04/이미지 |
| Windows 네이티브 Ollama | 미사용 | 2026-01-20 발표했지만 Windows 미지원 |

---

## 📂 파이프라인 구조

```
themes/neukgu/
├── theme.json                 # 테마 메타
├── preview.html               # 브라우저 비교 뷰어 (체커 + 다크 배경)
├── NOTES.md                   # 이 파일
└── assets/
    ├── idle.png               # 원본 레퍼런스 + idle 애셋
    ├── typing-f1/2/3.png      # working 상태 프레임 (정렬/투명 적용 후)
    ├── typing.apng            # 조립된 working 루프
    ├── thinking-f1/2/3.png    # thinking 프레임
    ├── thinking.apng          # thinking 루프
    ├── happy-f1/2/3.png       # happy 프레임 (노란 스파클 적용)
    ├── happy.apng             # happy 루프
    ├── *-v1.png / *.bak       # 구 버전 / 백업 (삭제 가능)
    └── aligned/               # 정렬된 프레임들 (중간 산출물)

scripts/neukgu/
├── gen-frame.py               # OpenRouter Nano Banana 호출 (--confirm 없으면 dry-run)
├── transparent-bg.py          # 흰 배경 → 투명 알파 변환 (border flood-fill + trapped-color tint)
├── align-frames.py            # 프레임 정렬 (bbox + ROI + x/y-anchor 지원)
├── assemble-apng.py           # PNG 시퀀스 → APNG 합성 (PIL)
├── find-eyes.py               # PNG에서 검은 점 클러스터 찾아 눈 위치 추출
├── erase-eyes.py              # PNG의 눈을 fur color로 지우기 (eye tracking용 배경 생성)
├── check-svg.py               # SVG 인코딩/BOM 점검 (디버깅용)
└── prompts/
    ├── typing-f1/2/3.txt
    ├── thinking-f1/2/3.txt
    └── happy-f1/2/3.txt
```

---

## 🔧 파이프라인 표준 순서 (상태 추가 시)

```
1. 프롬프트 작성 (f1: 큰 포즈, f2/f3: delta만)
2. gen-frame.py로 F1 생성 (사용자 승인 필수, --confirm)
3. 결과 확인 → OK면 F2, F3 병렬 생성 (F1을 anchor로)
4. transparent-bg.py --mode border --trapped-color 255,220,80  (스파클 색 필요시)
5. align-frames.py --x-anchor center --y-anchor bottom [--roi x0,y0,x1,y1]
6. assemble-apng.py --duration 180~220
7. theme.json에 상태 매핑 추가
8. userData/clawd-on-desk/themes/neukgu/ 로 배포
9. preview.html 업데이트
```

---

## 💡 교훈 (기억 저장됨)

### 1. API 호출 승인 프로토콜
- 1 프레임이라도 **절대 허락 없이 호출 금지**
- `gen-frame.py`는 `--confirm` 없으면 dry-run
- 비용 미리 표시 (예상 $0.04/이미지)

### 2. Freeze는 정밀하게, 전체 아님
- ❌ "FREEZE everything" (모델 혼란)
- ✅ "MUST STAY IDENTICAL: face, body, colors, outlines" + "CHANGE: tail, ears"
- 바뀌지 말아야 할 것 / 바뀌어야 할 것을 명시적으로 분리

### 3. Anchor 전략
- **Multi-turn chaining X, F1 anchor O** — F2/F3 모두 F1 레퍼런스. 드리프트 누적 방지
- 프롬프트 강화어 효과적: "PIXEL-IDENTICAL", "copy-paste identical"

### 4. Bbox 정렬은 필수 후처리
- Nano Banana는 프레임마다 sub-pixel 단위 wobble 생성
- `align-frames.py`로 반드시 정렬 후 APNG 조립
- **옵션 조합**:
  - `--x-anchor`: left/center/right
  - `--y-anchor`: top/center/bottom
  - `--roi x0,y0,x1,y1`: 정렬 계산 시 특정 영역만 참고
- **케이스별 best**:
  - typing: center/center (팔이 크게 안 움직임)
  - thinking: right/bottom (꼬리가 왼쪽에서 출렁임)
  - happy: center/bottom + ROI (몸통 코어) — 팔이 V 모양으로 움직이니 bbox 양끝 둘 다 흔들림

### 5. 투명 배경 처리 (border flood-fill)
- 단순 threshold → 갇힌 흰색 (스파클 내부) 같이 투명으로 바뀜 ❌
- **border flood-fill**: 이미지 가장자리에서 연결된 흰색만 투명 처리
- 갇힌 흰색 → 유지 (스파클 속, 눈 하이라이트 등)
- `--trapped-color 255,220,80` 옵션으로 갇힌 흰색을 특정 색으로 tint (노란 스파클 등)

### 6. 정렬 시 RGBA 투명 fill 주의
- `align-frames.py`의 shift에서 노출된 가장자리를 **투명(0,0,0,0)으로 채워야 함**
- 불투명 흰색 채우면 apng에 흰색 strip 자국 생김

### 7. ROI 정렬
- 포즈 변형(팔 움직임 등)이 bbox 양끝을 흔들면 center/edge 전역 정렬 불가
- **ROI로 안정 영역(몸통 코어)만 bbox 계산 기준 삼기**
- happy의 경우 ROI 250,500,700,870 = 팔 위쪽 + 꼬리 오른쪽 제외

### 8. Eye Tracking 하이브리드 (PNG + SVG overlay)
**구조**:
```
<svg viewBox="0 0 200 200">
  <g id="shadow-js">  <!-- 바닥 타원 그림자 --> </g>
  <g id="body-js">    <!-- 눈 지운 PNG 임베드 --> </g>
  <g id="eyes-js">    <!-- 오버레이 눈 2개 (translate로 이동) --> </g>
</svg>
```
**핵심 트릭**: 원본 PNG의 눈을 `erase-eyes.py`로 fur color 원으로 덮어서 "눈 없는 버전" 만들고, 그 위에 SVG 오버레이 눈을 얹음. 오버레이가 어디로 이동하든 원본 눈 보일 걱정 없음.

**튜닝 값 (현 설정)**:
- `maxOffset: 2.0` (viewBox 200 기준 1%) — 미세하지만 인지 가능
- `bodyScale: 0.2` (몸은 눈의 20%만 움직임 = 살짝 lean)
- 오버레이 ellipse rx=2.7, ry=3.6 (PNG eye 3.0x4.0 대비 약간 작게, 부담감 줄임)

**눈 좌표 찾기**: `find-eyes.py`로 자동 검출 (검은 픽셀 클러스터 중 outline 제외한 작은 것 2개 = 눈)

### 9. Clawd 외부 테마 SVG 특유 이슈 (중요!)
- **XML 선언 제거 필수**: `<?xml ... ?>` 있으면 Clawd sanitizer(htmlparser2+dom-serializer)가 `?>`를 잘라먹어 "error on line 1" 파싱 실패
- **상대 href 주의**: 외부 테마 SVG는 `theme-cache/<id>/assets/`로 복사되지만 PNG는 소스에 남아 상대경로 깨짐
  - 임시 해결: PNG를 cache 디렉토리에도 수동 복사
  - 근본 해결: built-in으로 이동 or Clawd PR (비-SVG 자산도 cache 복사)
- **Cache 강제 재빌드**: 캐시된 SVG 업데이트하려면 `rm {userData}/theme-cache/<id>/assets/<file>.svg` 후 테마 재로드

---

## ⚠️ Clawd 테마 시스템 필수사항

- `schemaVersion: 1`, `name`, `version` 필수
- **REQUIRED_STATES**: `idle`, `working`, `thinking`, `sleeping`, `waking` — 다 있어야 테마 로드됨 (없으면 fallback으로 다른 상태 가리키기)
- **sleepSequence.mode**: `full`이면 yawning/dozing/collapsing 필수, `direct`면 생략 가능 (MVP는 `direct` 사용)
- **viewBox**: SVG 단위 로직 캔버스. 애셋의 aspect ratio와 맞춰야 함
- **hitBoxes.default** 필수
- Asset 경로는 assets/ 기준 파일명만 (디렉토리 분리 가능)

---

## 🎨 테마 파일 현재 상태 (theme.json)

```json
{
  "schemaVersion": 1,
  "viewBox": { "x": 0, "y": 0, "width": 200, "height": 200 },
  "eyeTracking": {
    "enabled": true,
    "states": ["idle"],
    "maxOffset": 2.0,          ← 눈 움직임 범위
    "bodyScale": 0.2,          ← 몸은 눈의 20% 움직임
    "ids": { "eyes": "eyes-js", "body": "body-js", "shadow": "shadow-js" },
    ...
},
  "states": {
    "idle":      ["idle.png"],
    "working":   ["typing.apng"],
    "thinking":  ["thinking.apng"],
    "attention": ["happy.apng"],
    "sleeping":  ["idle.png"],   ← 폴백, 실 애셋 나오면 교체
    "waking":    ["idle.png"]
  },
  "sleepSequence": { "mode": "direct" },
  "hitBoxes": { "default": { "x": 30, "y": 30, "w": 140, "h": 150 } },
  "miniMode": { "supported": false }
}
```

---

## 🔑 API 키 보안

- 사용자가 OpenRouter 키 제공 (세션 환경변수로만 사용)
- **프로젝트 종료 후 rotate 권장** — 대화 기록에 노출됨
- 파일/스크립트/.env/git에 절대 저장 안 함

---

## 🚀 다음 단계

1. **MVP 마무리** (남은 3개, $0.24~0.36)
   - `notification` (알림 기능, 귀 쫑긋 + "!" 심볼)
   - `error` (에러 발생, 당황한 표정 + "X" 또는 "!?" 심볼)
   - `sleeping` (누워서 잠, Z 심볼)
2. **Eye Tracking SVG** (idle 상태에 마우스 추적)
3. **Tier 2+**: sleep 시퀀스, working 변형, 리액션, mini mode
