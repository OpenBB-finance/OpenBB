## 빠른 실행 순서 (Quant Lab)

### 백엔드 서버 열기 (OpenBB API)

PowerShell 창 1개에서 실행:

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
.\.venv\Scripts\Activate.ps1
openbb-api --host 127.0.0.1 --port 6900
```

- 백엔드 주소: `http://127.0.0.1:6900`
- 확인용: `http://127.0.0.1:6900/docs`

### 프론트 서버 열기 (Desktop Web)

PowerShell 창을 하나 더 열고 실행:

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop\desktop"
npm run dev
```

- 프론트 주소: `http://localhost:1470`
- Quant Lab 바로가기: `http://localhost:1470/quant`

### 한 번에 두 서버 실행 (권장)

루트 폴더에서 아래를 실행하면 PowerShell 2개가 자동으로 열립니다.

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
.\start_all.ps1
```

> 주의: PowerShell에서는 `start_all.ps1`만 입력하면 실행되지 않습니다. 
반드시 `.\start_all.ps1` 형태로 실행해야 합니다.

### 사용/종료

1. 브라우저에서 `http://localhost:1470/quant` 접속
2. 화면에서 `학습 실행 -> 신호 생성 -> 백테스트 실행`
3. 종료할 때는 두 PowerShell 창에서 각각 `Ctrl + C`

### 안 열릴 때 빠른 점검

```powershell
netstat -ano | findstr :6900
netstat -ano | findstr :1470
```

- `LISTENING`이 보이지 않으면 해당 서버를 다시 실행
---
# OpenBB ODP 사용 가이드

## ⚡ 간단 실행

1. **`openbb_실행.bat`** 더블클릭
2. 또는 터미널에서:
   ```powershell
   cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
   .\.venv\Scripts\Activate.ps1
   openbb
   ```

---

[OpenBB 문서](https://docs.openbb.co/)를 기반으로 정리한 설치 및 사용법입니다.

---

## ✅ 설치 완료 상태

다음이 설치되어 있습니다:
- **ODP Python** (소스에서 빌드) - Python API
- **ODP CLI** - 터미널 인터페이스
- 모든 확장 프로그램 및 데이터 공급자

---

## 🚀 실행 방법

### 1. OpenBB CLI 실행 (중요!)

**"지정된 경로를 찾을 수 없다" / "openbb을(는) 찾을 수 없습니다"** 에러가 나면 → 가상 환경이 활성화되지 않은 것입니다.

**방법 A: 가상환경 활성화 후 실행 (권장)**

1. PowerShell을 **관리자 권한 없이** 열기
2. 프로젝트 폴더로 이동:
   ```powershell
   cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
   ```
3. 가상환경 활성화:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(성공하면 프롬프트 앞에 `(.venv)` 가 붙습니다)*
4. openbb 실행:
   ```powershell
   openbb
   ```

**방법 B: 가상환경 없이 직접 실행**

프로젝트 폴더에서:
```powershell
.\.venv\Scripts\openbb.cmd
```

**방법 C: Python 모듈로 실행**

```powershell
.\.venv\Scripts\python.exe -m openbb_cli.cli
```

> ⚠️ Activate.ps1 실행이 거부되면: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 먼저 실행 후 다시 시도

**"지정된 경로를 찾을 수 없습니다" 지속 시 (한글 경로 이슈):**

1. **`openbb_실행.bat`** 더블클릭 — 작업 디렉터리를 `C:\Users\yygg1`로 바꿔 실행
2. **system_settings.json**에 `"headless": true` 추가 — 차트 창 없이 실행 (이미 적용됨)
3. 위 방법으로도 안 되면 프로젝트를 **한글이 없는 경로**(예: `C:\OpenBB-develop`)로 이동 후 재설치

### 2. ODP Python (Python/Jupyter에서)

```python
from openbb import obb

# 주식 시세 조회
quote = obb.equity.price.quote(symbol="AAPL", provider="yfinance")
print(quote.to_df())

# 과거 주가 데이터
df = obb.equity.price.historical(symbol="AAPL", provider="yfinance").to_df()

# 기술적 분석 (예: Donchian Channel)
output = obb.equity.price.historical(symbol="AAPL", provider="yfinance")
ta = obb.technical.donchian(data=output.results).to_df()
```

### 3. ODP CLI 정상 실행 확인

위 1번 방법으로 `openbb`를 실행하면 터미널에 OpenBB CLI 홈 화면이 나타납니다. 메뉴를 탐색하며 데이터를 조회할 수 있습니다.

---

## 🔄 버전 업데이트 (개발자가 새 버전 릴리스 시)

### ZIP으로 받은 경우 → Git 저장소로 바꾸기 (1회만)

**`git_변환.ps1`** 더블클릭하면 자동 변환됩니다. (우클릭 → PowerShell에서 실행)

또는 수동으로:

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"

# 1. 커스텀 파일 백업 (홈 폴더에 보관)
Copy-Item openbb_실행.bat $env:USERPROFILE\openbb_실행.bat.bak
Copy-Item OpenBB_사용가이드.md $env:USERPROFILE\OpenBB_사용가이드.md.bak

# 2. Git 저장소로 전환
git init
git remote add origin https://github.com/OpenBB-finance/OpenBB.git
git fetch origin develop
git checkout -b develop origin/develop

# 3. 백업 파일 복원
Copy-Item $env:USERPROFILE\openbb_실행.bat.bak openbb_실행.bat -Force
Copy-Item $env:USERPROFILE\OpenBB_사용가이드.md.bak OpenBB_사용가이드.md -Force
Remove-Item $env:USERPROFILE\openbb_실행.bat.bak, $env:USERPROFILE\OpenBB_사용가이드.md.bak
```

### 일반 업데이트 (Git 저장소로 전환 후)

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
.\.venv\Scripts\Activate.ps1

# 1. 최신 코드 가져오기
git pull origin develop

# 2. 의존성 및 패키지 재설치
cd openbb_platform
python dev_install.py -e --cli
cd ..

# 3. (선택) 정적 에셋 재빌드
openbb-build
```

**참고:** `develop` 브랜치가 아니라 다른 브랜치(예: `main`)를 쓰는 경우 `git pull origin main`처럼 브랜치명을 맞춰 주세요.

---

## 📤 원격 저장소 역할 및 작업 흐름

### 원격 저장소 역할 정리

| 원격 이름 | 저장소 | 용도 |
|-----------|--------|------|
| `origin` | OpenBB 공식 (OpenBB-finance/OpenBB) | 업데이트 받기 |
| `myrepo` | 내 비공개 저장소 (ryun6249/OpenBB-develop-ML) | 내 변경사항 올리기 |

### 최초 1회: 내 GitHub 저장소 연결

1. https://github.com/new 에서 **Private** 저장소 `OpenBB-develop-ML` 생성
2. 아래 명령 실행:

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
git remote add myrepo https://github.com/ryun6249/OpenBB-develop-ML.git
git push -u myrepo develop
```

### 이후 작업 흐름

| 할 일 | 명령 |
|-------|------|
| OpenBB 최신 버전 받기 | `git pull origin develop` |
| 내 변경사항 GitHub에 올리기 | `git add .` → `git commit -m "메시지"` → `git push myrepo develop` |
| 업데이트 후 패키지 재설치 | `cd openbb_platform` → `python dev_install.py -e --cli` |

### 수동 업로드(권장, 실무 절차)

아래 절차를 그대로 실행하면 로컬 변경을 `myrepo/develop`에 안전하게 올릴 수 있습니다.

1. 작업 위치/브랜치/원격 확인

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
git status --short
git branch --show-current
git remote -v
```

2. 불필요 산출물은 제외하고 필요한 경로만 스테이징

```powershell
# 예시: 프론트 + quant_ml 확장만 올릴 때
git add desktop openbb_platform/extensions/quant_ml
```

3. 커밋 생성

```powershell
git commit -m "feat: 변경 내용 요약"
```

4. 내 저장소(`myrepo`)의 `develop` 브랜치로 푸시

```powershell
git push myrepo develop
```

5. 푸시 후 확인

```powershell
git status --short
```

`logs/`, `OpenBB/` 같은 로컬 임시 폴더가 남아도, 스테이징하지 않았다면 GitHub에는 올라가지 않습니다.

---

## 📋 당신이 해야 할 일

### 1. API 키 설정 (권장)

많은 데이터 제공자(FMP, Benzinga, FRED 등)는 API 키가 필요합니다.  
설정 파일 위치: `~/.openbb_platform/user_settings.json`

**yfinance**는 API 키 없이 기본 기능을 사용할 수 있습니다.

필요한 경우 아래 예시처럼 설정할 수 있습니다:

```json
{
  "credentials": {
    "fmp_api_key": "여기에_FMP_키",
    "fred_api_key": "여기에_FRED_키",
    "alpha_vantage_api_key": "여기에_알파_벤티지_키"
  }
}
```

API 키 발급:
- [FMP](https://site.financialmodelingprep.com/developer/docs/) 
- [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
- [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

### API 키 작성란 바로 열기

```powershell
notepad "$HOME\\.openbb_platform\\user_settings.json"
```

필수 키 이름(정확히 동일):

```json
{
  "credentials": {
    "fmp_api_key": "YOUR_FMP_KEY",
    "fred_api_key": "YOUR_FRED_KEY",
    "alpha_vantage_api_key": "YOUR_ALPHA_VANTAGE_KEY"
  }
}
```

### API 연결 상태 점검/복구 절차 (권장)

아래 순서대로 하면 `FRED/FMP/Alpha Vantage` 연결 상태를 한 번에 점검할 수 있습니다.

1. `user_settings.json` 인코딩 점검(BOM 제거)

```powershell
$p = "$HOME\\.openbb_platform\\user_settings.json"
$bytes = [System.IO.File]::ReadAllBytes($p)
if ($bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
  $txt = [System.IO.File]::ReadAllText($p)
  $enc = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($p, $txt, $enc)
  "BOM 제거 완료"
} else {
  "이미 UTF-8(BOM 없음)"
}
```

2. 백엔드 실행/포트 확인

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in 6900,6901 }
```

`6901`로 떠 있다면 아래 URL의 포트를 `6901`로 바꿔서 테스트하면 됩니다.

3. OpenBB API로 provider 연결 테스트

```powershell
# FMP
curl "http://127.0.0.1:6900/api/v1/equity/profile?symbol=AAPL&provider=fmp"

# Alpha Vantage
curl "http://127.0.0.1:6900/api/v1/equity/price/historical?symbol=IBM&provider=alpha_vantage&start_date=2025-01-01&end_date=2025-01-31"

# FRED (Macro)
curl "http://127.0.0.1:6900/api/v1/quant_ml/macro/series?key=FRED:DGS10&start=2024-01-01&end=2024-12-31&freq=W&fill=ffill"
```

4. Macro preset 동작 확인 (Copper/Gold + 10Y)

```powershell
curl "http://127.0.0.1:6900/api/v1/quant_ml/macro/presets/copper_gold?start=2024-01-01&end=2024-12-31&freq=W"
```

5. FRED 키가 캐시 경고로 나오면

- 백엔드를 재시작하고 다시 3~4를 실행합니다.
- 이 확장은 `~/.openbb_platform/user_settings.json`의 `credentials.fred_api_key`도 자동 인식합니다.

### 전체 연결 상태 1회 점검(복붙용)

```powershell
curl "http://127.0.0.1:6900/api/v1/quant_ml/health"
curl "http://127.0.0.1:6900/api/v1/quant_ml/macro/health"
curl "http://127.0.0.1:6900/api/v1/quant_ml/macro/presets/copper_gold?start=2024-01-01&end=2024-12-31&freq=W"
curl "http://127.0.0.1:6900/api/v1/economy/fred_series?symbol=DGS10&provider=fred&start_date=2025-01-01&end_date=2025-01-31"
curl "http://127.0.0.1:6900/api/v1/equity/profile?symbol=AAPL&provider=fmp"
curl "http://127.0.0.1:6900/api/v1/equity/price/historical?symbol=IBM&provider=alpha_vantage&start_date=2025-01-01&end_date=2025-01-31"
```

정상 기준:
- 모두 `200 OK` 응답
- `quant_ml/macro/presets/copper_gold` 응답에서 `series` 2개 이상
- `quant_ml/macro/health` 응답에서 `status=ok` 또는 경고 메시지 포함(`insufficient_data` 원인 확인 가능)

### Quant 운영잡/베이스라인 실행 절차 (신규)

1. 운영 잡 수동 1회 점검 (`ops_jobs.yaml` 사용)

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
$env:PYTHONPATH='openbb_platform/extensions/quant_ml'
python -m openbb_quant_ml.jobs.cli daily --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
python -m openbb_quant_ml.jobs.cli weekly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
python -m openbb_quant_ml.jobs.cli monthly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
```

2. Task Scheduler 등록(Windows)

```powershell
$repo = "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
$cfg  = "openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml"

$jobRoot = "C:\quantml_jobs"
New-Item -ItemType Directory -Force -Path $jobRoot | Out-Null

@"
Set-Location "$repo"
$env:PYTHONPATH = "openbb_platform/extensions/quant_ml"
python -m openbb_quant_ml.jobs.cli daily --config "$cfg"
"@ | Set-Content -Path "$jobRoot\quantml_daily.ps1" -Encoding UTF8

@"
Set-Location "$repo"
$env:PYTHONPATH = "openbb_platform/extensions/quant_ml"
python -m openbb_quant_ml.jobs.cli weekly --config "$cfg"
"@ | Set-Content -Path "$jobRoot\quantml_weekly.ps1" -Encoding UTF8

@"
Set-Location "$repo"
$env:PYTHONPATH = "openbb_platform/extensions/quant_ml"
python -m openbb_quant_ml.jobs.cli monthly --config "$cfg"
"@ | Set-Content -Path "$jobRoot\quantml_monthly.ps1" -Encoding UTF8

schtasks /Create /F /TN "QuantML-Daily"   /SC DAILY   /ST 18:30 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\quantml_jobs\quantml_daily.ps1"
schtasks /Create /F /TN "QuantML-Weekly"  /SC WEEKLY  /D SAT /ST 08:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\quantml_jobs\quantml_weekly.ps1"
schtasks /Create /F /TN "QuantML-Monthly" /SC MONTHLY /D 1   /ST 09:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\quantml_jobs\quantml_monthly.ps1"
```

3. 소규모 E2E 후 베이스라인 스냅샷 생성

- 학습/신호/백테스트를 1회 완료한 다음:

```powershell
cd "C:\Users\yygg1\OneDrive\바탕 화면\bot\OpenBB-develop"
$env:PYTHONPATH='openbb_platform/extensions/quant_ml'
python -m openbb_quant_ml.service.baseline_snapshot --run-id <RUN_ID> --period 1y --symbols-count 20 --target-mode next_open_to_close --entry-price next_open --exit-price close
```

- `RUN_ID` 확인:

```powershell
curl "http://127.0.0.1:6900/api/v1/quant_ml/health"
```

응답의 `resolved_run_id`를 사용하면 됩니다.

- 결과 파일:
  - `~/.openbb_platform/quant_ml/runs/<RUN_ID>/time_profile.json`
  - `~/.openbb_platform/quant_ml/runs/<RUN_ID>/metrics.json`
  - `~/.openbb_platform/quant_ml/baselines/baseline_*.json`

### 2. ODP Desktop (선택)

그래픽 환경이 필요하면:
- [ODP Desktop 다운로드](https://github.com/OpenBB-finance/OpenBB/releases/tag/ODP)
- 설치 후 API Keys 화면에서 키 등록
- Backends에서 `OpenBB API` 시작 → Workspace에서 `http://127.0.0.1:6900` 연결

### 3. Docker 사용 (선택)

```powershell
docker build -f build/docker/platformAPI.Dockerfile -t openbb-platform:latest .
docker run -it --rm -p 6900:6900 -v ~/.openbb_platform:/root/.openbb_platform openbb-platform:latest
```

---

## 📖 CLI 사용법 요약

| 동작 | 입력 |
|------|------|
| 메뉴 들어가기 | `economy` 등 메뉴 이름 입력 |
| 상위로 | `..` 또는 `q` |
| 홈으로 | `/` 또는 `home` |
| 다른 메뉴로 이동 | `/equity/price/historical` (절대 경로) |
| 도움말 | `--help` 또는 `-h` |
| 파라미터 | `--기호 AAPL --시작일 2024-01-01` |
| **주의**: 위치 인자 없음 | ❌ `historical AAPL` / ✅ `historical --symbol AAPL` |

**예시 명령:**
```
/equity/price/historical --symbol SPY --start_date 2024-01-01 --provider yfinance
/technical/rsi --data OBB0 --chart
/economy/calendar --provider nasdaq --country united_states
```

---

## 📚 참고 링크

- [ODP Python 문서](https://docs.openbb.co/odp/python)
- [ODP CLI 문서](https://docs.openbb.co/odp/cli)
- [ODP Desktop 문서](https://docs.openbb.co/odp/desktop)
- [API 키 설정](https://docs.openbb.co/odp/python/settings/user_settings/api_keys)
