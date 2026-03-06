# QA Scripts

프로젝트 품질 보증(QA) 및 검증 스크립트 모음입니다.

## 검증 파이프라인 (PowerShell)

| 스크립트 | 용도 | 호출 방법 |
|---------|------|----------|
| `run_full_verification.ps1` | **전체 프로젝트 검증** — linting, 타입 체크, pytest, CI gate 전체 실행 | `.\qa\scripts\run_full_verification.ps1` |
| `quant_ml_verify_full.ps1` | **Quant ML 전용 검증** — ML 테스트, API smoke, 프론트엔드 tsc | `.\qa\scripts\quant_ml_verify_full.ps1 -SessionId "test-001"` |
| `run_integration_gate.ps1` | **프로바이더 통합 테스트** — OpenBB API 프로바이더별 통합 검증 | `.\qa\scripts\run_integration_gate.ps1` |
| `run_integration_gate_background.ps1` | 위 스크립트의 백그라운드 래퍼 | 자동 호출 |
| `quant_ml_overnight_runner.ps1` | **야간 자동 실행** — 전체 학습+검증 파이프라인 | 스케줄러에서 호출 |
| `quant_ml_recover_state.ps1` | 학습 실패 시 상태 복구 | `.\qa\scripts\quant_ml_recover_state.ps1` |

## 결과 수집 (Python)

| 스크립트 | 용도 |
|---------|------|
| `collect_results.py` | `run_full_verification` 결과를 JSON+Markdown 보고서로 변환 |
| `quant_ml_collect_report.py` | `quant_ml_overnight_runner` 결과를 최종 보고서로 생성 |

## 코드 생성 / 계약 관리 (Python)

| 스크립트 | 용도 |
|---------|------|
| `generate_quant_ts_types.py` | Pydantic 모델에서 TypeScript 인터페이스 자동 생성 |
| `quant_ml_contract_inventory.py` | 백엔드 모델 계약 인벤토리 CSV 생성 |
| `quant_ml_frontend_contract_inventory.py` | 프론트엔드 타입 계약 인벤토리 CSV 생성 |
| `quant_api_templates.ps1` | API 엔드포인트 템플릿 및 테스트 데이터 |

## 설정 파일 (`qa/config/`)

- `verification_targets.yaml` — 검증 대상 경로 및 옵션
- `provider_tiers.yaml` — 프로바이더 tier 분류 (core/extended) 및 재시도 정책
