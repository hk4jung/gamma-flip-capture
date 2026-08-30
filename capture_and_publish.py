#!/usr/bin/env python3
"""GitHub Actions에서 실행: NQ/ES를 Playwright로 캡처해서 CSV로 남긴다.

서버로 직접 보내지 않는다(push 아님) — 이 저장소에 커밋해서 공개하고,
서버가 raw.githubusercontent.com에서 그냥 GET으로 가져가게 한다(pull).
서버 쪽에 쓰기 가능한 엔드포인트를 만들지 않기 위한 설계다.

실제 git add/commit/push는 워크플로우(.github/workflows/capture.yml)가 한다.
이 스크립트는 캡처 로직 + 캡처 시각 메타데이터 기록만 담당한다.

캡처 로직은 gamma_flip.py의 run_capture_sync()를 그대로 재사용한다(중복 구현 없음).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamma_flip as gf  # noqa: E402

CSV_PATH = "barchart_options_capture.csv"
META_PATH = "capture_meta.json"


def main():
    print("[1/2] NQ/ES 캡처 중 (Playwright, ubuntu-latest — glibc 문제 없음)...")
    gf.run_capture_sync(["NQ", "ES"], CSV_PATH)

    if not os.path.exists(CSV_PATH):
        sys.exit("캡처 실패: CSV 파일이 생성되지 않았습니다. 위 로그를 확인하세요.")

    print("[2/2] 캡처 시각 메타데이터 기록...")
    now = time.time()
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "captured_at_epoch": now,
            "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        }, f)

    print("완료. git 커밋/푸시는 워크플로우 yml이 이어서 처리합니다.")


if __name__ == "__main__":
    main()
