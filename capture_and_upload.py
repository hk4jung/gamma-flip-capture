#!/usr/bin/env python3
"""GitHub Actions에서 실행: NQ/ES를 Playwright로 캡처해서 CSV로 만들고,
gamma_flip 서버의 /internal/upload_futures_csv 로 업로드한다.

캡처 로직은 gamma_flip.py의 run_capture_sync()를 그대로 재사용한다(중복 구현 없음).
GitHub Actions의 ubuntu-latest 러너는 최신 glibc라 Playwright/Chromium이
아무 문제 없이 뜬다 — 오래된 서버(Ubuntu 16.04)에서 Docker 없이 못 하던 걸
여기서 대신 해주는 것이 이 워크플로우의 존재 이유다.

필요한 환경변수 (GitHub Secrets로 설정):
  UPLOAD_URL   예: https://xmpp1530.cafe24.com/gamma_flip/internal/upload_futures_csv
  UPLOAD_TOKEN 서버의 FUTURES_UPLOAD_TOKEN 환경변수와 동일한 값
"""
import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamma_flip as gf  # noqa: E402

CSV_PATH = "barchart_options_capture.csv"


def main():
    upload_url = os.environ["UPLOAD_URL"]
    upload_token = os.environ["UPLOAD_TOKEN"]

    print(f"[1/2] NQ/ES 캡처 중 (Playwright, ubuntu-latest)...")
    gf.run_capture_sync(["NQ", "ES"], CSV_PATH)

    if not os.path.exists(CSV_PATH):
        sys.exit("캡처 실패: CSV 파일이 생성되지 않았습니다. 위 로그를 확인하세요.")

    with open(CSV_PATH, "rb") as f:
        data = f.read()
    print(f"      CSV 크기: {len(data)} bytes")

    print(f"[2/2] 서버로 업로드 중: {upload_url}")
    resp = requests.post(
        upload_url, data=data,
        headers={"X-Upload-Token": upload_token, "Content-Type": "text/csv"},
        timeout=30,
    )
    print(f"      응답: {resp.status_code} {resp.text[:300]}")
    resp.raise_for_status()
    print("완료.")


if __name__ == "__main__":
    main()
