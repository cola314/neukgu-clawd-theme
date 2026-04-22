# 늑구 (Neukgu) — Clawd on Desk 테마

A cute cartoon wolf desktop pet theme for [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk).

Idle 상태에 마우스 눈 추적 지원. Typing / Thinking / Happy 애니 포함.

## 🎬 미리보기

| idle (eye tracking) | thinking 🤔 | working 💻 | happy ✨ |
|:---:|:---:|:---:|:---:|
| ![idle](assets/idle.png) | ![thinking](assets/thinking.apng) | ![working](assets/typing.apng) | ![happy](assets/happy.apng) |

## 📦 설치

### 방법 1 — git clone

```bash
# Windows (PowerShell / Git Bash)
git clone https://github.com/cola314/neukgu-clawd-theme \
  "$APPDATA/clawd-on-desk/themes/neukgu"

# macOS
git clone https://github.com/cola314/neukgu-clawd-theme \
  "$HOME/Library/Application Support/clawd-on-desk/themes/neukgu"

# Linux
git clone https://github.com/cola314/neukgu-clawd-theme \
  "$HOME/.config/clawd-on-desk/themes/neukgu"
```

### 방법 2 — ZIP 다운로드

1. 이 리포에서 `Code → Download ZIP`
2. 압축 해제 후 폴더명을 `neukgu`로 변경
3. Clawd의 `userData/themes/` 하위로 복사 (위 경로 참조)

### ⚠️ PNG 참조 이슈 우회

Clawd는 외부 테마의 SVG만 `theme-cache` 로 복사하고 PNG는 원본 dir에 두기 때문에, SVG의 `<image href="idle-eyeless.png">` 상대 경로가 깨집니다. 설치 후 **한 번 수동으로 PNG를 cache에도 복사**해주세요:

```bash
# Windows
cp "$APPDATA/clawd-on-desk/themes/neukgu/assets/idle-eyeless.png" \
   "$APPDATA/clawd-on-desk/theme-cache/neukgu/assets/"
```

(Clawd 본체가 비-SVG 자산도 캐시 복사하도록 업데이트되면 이 단계는 필요 없어집니다.)

## 🎮 테마 활성화

1. Clawd 재시작
2. 우클릭 → **Theme** → **늑구 (Neukgu)** 선택

## 🎨 상태 매핑

| 상태 | 트리거 | 애니 |
|------|-------|------|
| `idle` | 기본 | 정적 + 마우스 눈 추적 |
| `working` | PreToolUse (툴 실행) | 3프레임 타이핑 루프 |
| `thinking` | UserPromptSubmit (프롬프트 입력) | 3프레임 꼬리 흔들기 + 흰 "?" |
| `attention` | Stop (작업 완료) | 3프레임 cheer wave + 노란 스파클 |
| `sleeping` | 절전 | idle 폴백 (TODO) |
| `notification` / `error` | TODO | — |

## 🛠️ 커스터마이징 & 재생성

`scripts/`에 AI 생성 파이프라인 전체 포함:

- `gen-frame.py` — OpenRouter Nano Banana 호출 (승인 후 `--confirm`으로 실행)
- `transparent-bg.py` — border flood-fill로 흰 배경 투명화 + 갇힌 흰색 컬러 tint
- `align-frames.py` — bbox/ROI 기반 프레임 정렬 (흔들림 제거)
- `assemble-apng.py` — PIL로 APNG 합성
- `erase-eyes.py` — eye tracking용 PNG 눈 제거
- `recolor-symbol.py` — 특정 영역 다크 클러스터 재채색 (예: "?" 를 흰색으로)
- `find-eyes.py` — PNG 눈 좌표 자동 검출
- `check-*.py` — 알파/픽셀/SVG 디버깅 툴

### 새 상태 만드는 흐름

```
1. prompts/<state>-f1.txt ... f3.txt 프롬프트 작성
2. gen-frame.py로 F1 생성 → 사용자 승인 → F2/F3 병렬 생성
3. transparent-bg.py --mode border (필요시 --trapped-color)
4. align-frames.py --x-anchor <...> --y-anchor <...> [--roi ...]
5. assemble-apng.py --duration <ms>
6. theme.json states에 추가
```

자세한 기록은 [NOTES.md](NOTES.md) 참조.

## 📝 라이선스 / Attribution

- **Theme code & scripts**: MIT License (`LICENSE` 파일 참조)
- **Character artwork**:
  - 베이스 레퍼런스 (`assets/idle.png`): ChatGPT (OpenAI DALL-E) 생성
  - 애니메이션 프레임 (`typing.apng` / `thinking.apng` / `happy.apng`): Google **Nano Banana** (Gemini 2.5 Flash Image) 생성
- 전체 파이프라인 제작 지원: [Claude Code](https://claude.com/claude-code)

## 💸 만들 때 든 비용

- AI 이미지 생성 (OpenRouter Nano Banana): **약 $0.52** (≈ 735원) — 13 프레임 × $0.04
- 로컬 처리 (투명 배경, 정렬, APNG 합성, SVG 제작): $0

## 🐺 Made with 늑구 + Claude Code

작업 과정, 파이프라인 선택, 튜닝 값 등은 [NOTES.md](NOTES.md)에 상세 기록되어 있습니다.
