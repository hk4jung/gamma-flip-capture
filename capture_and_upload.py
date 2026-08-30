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
