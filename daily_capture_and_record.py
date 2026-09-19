#!/usr/bin/env python3
"""
daily_capture_and_record.py
============================
capture_and_publish.py를 대체하는 GitHub Actions용 일일 캡처 스크립트.
capture.yml에서 매일 한국시간(KST) 10:30에 실행되도록 예약돼 있습니다
(cron은 UTC 기준이라 '30 1 * * *' = UTC 01:30 = KST 10:30).

하는 일 세 가지:

  1) (기존과 동일) NQ/ES 옵션체인을 Barchart에서 캡처해
     barchart_options_capture.csv / capture_meta.json을 그대로 갱신한다.
     — app.py(Flask 웹 서비스)가 GET으로 당겨가는 "현재 스냅샷" 파일이라
       이름/형식/위치를 절대 바꾸지 않는다.

  2) 오늘자(한국시간 기준) 스냅샷을 archive/ 아래에 날짜가 들어간 파일명으로
     따로 저장한다: archive/barchart_options_capture_YYYY-MM-DD.csv
     원본 컬럼은 그대로 두고 "download_date_kst"(YYYY-MM-DD)와
     "download_datetime_kst"(YYYY-MM-DD HH:MM:SS) 두 컬럼만 덧붙여서,
     이 보관 파일 하나만 열어봐도 언제 받은 데이터인지 알 수 있게 한다.

  3) NQ/ES 각각에 대해 gamma_flip.py의 run_futures_mode()와 완전히 같은 계산
     (Black-76 스캔 → 감마 플립 레벨 / 순 GEX / 레짐, 콜월·풋월 단일최댓값 +
     스무딩)을 수행해서, 심볼별로 이름이 고정된 파일에 하루 한 행씩 누적
     기록한다: gamma_flip_nq_history.csv / gamma_flip_es_history.csv.
     같은 날 여러 번 실행되면(수동 workflow_dispatch 등) 그날 행을 최신
     값으로 덮어쓴다 — 하루에 행이 여러 개 쌓이지 않는다.

     ※ 이 계산은 외부 API를 더 부르는 게 아니라, 이 스크립트가 gamma_flip.py의
     함수(load_futures_symbol / derive_effective_iv_futures /
     compute_gex_curve_futures_bs / find_flip_point /
     compute_current_gex_from_barchart_gamma / find_walls_futures_raw /
     find_walls_futures_smoothed)를 호출해 GitHub Actions 러너 안에서 직접
     계산한 값이다 (아래 summarize_symbol() 참고).

한국시간은 GitHub Actions 러너의 시스템 시간대(UTC)와 무관하게 Python
zoneinfo로 직접 계산하므로, 러너 설정과 상관없이 항상 정확하다.
"""
import json
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamma_flip as gf  # noqa: E402  (sys.path 설정 뒤에 임포트해야 함)

CSV_PATH = "barchart_options_capture.csv"
META_PATH = "capture_meta.json"
ARCHIVE_DIR = "archive"
SYMBOLS = ["NQ", "ES"]
HISTORY_PATHS = {
    "NQ": "gamma_flip_nq_history.csv",
    "ES": "gamma_flip_es_history.csv",
}
KST = ZoneInfo("Asia/Seoul")

# run_futures_mode()가 쓰는 기본값과 정확히 맞춘다 (숫자가 똑같이 나오게).
RISK_FREE_RATE = 0.04
RANGE_PCT = 0.15
MIN_IV_ROWS = gf.FUTURES_MIN_IV_ROWS_DEFAULT
WALL_BANDWIDTH_PCT = gf.FUTURES_WALL_BANDWIDTH_PCT_DEFAULT

# symbol은 파일명(gamma_flip_nq_history.csv / gamma_flip_es_history.csv)이
# 이미 구분해주므로 컬럼에는 넣지 않는다.
HISTORY_COLUMNS = [
    "date_kst", "datetime_kst", "spot", "mode",
    "net_gex", "regime", "gamma_flip_level", "flip_distance_pt", "flip_distance_pct",
    "call_wall", "call_wall_oi", "put_wall", "put_wall_oi",
    "call_wall_smoothed", "call_wall_smoothed_oi", "put_wall_smoothed", "put_wall_smoothed_oi",
]


def summarize_symbol(symbol: str, now_kst: datetime) -> dict:
    """gamma_flip.py의 run_futures_mode()와 동일한 계산을 수행하고, 화면 출력
    대신 결과를 dict로 돌려준다 (히스토리 CSV의 한 행이 됨)."""
    chain, spot, multiplier = gf.load_futures_symbol(CSV_PATH, symbol)
    chain = gf.derive_effective_iv_futures(chain, spot, r=RISK_FREE_RATE)

    n_eff_calls = int(((chain["type"] == "call") & chain["iv_effective"].notna()).sum())
    n_eff_puts = int(((chain["type"] == "put") & chain["iv_effective"].notna()).sum())
    n_gamma = int(chain["gamma_barchart"].notna().sum())
    use_bs_mode = n_eff_calls >= MIN_IV_ROWS and n_eff_puts >= MIN_IV_ROWS

    row = {c: None for c in HISTORY_COLUMNS}
    row["date_kst"] = now_kst.strftime("%Y-%m-%d")
    row["datetime_kst"] = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    row["spot"] = round(float(spot), 2)

    if use_bs_mode:
        price_grid, gex_values = gf.compute_gex_curve_futures_bs(
            chain, spot, multiplier, RISK_FREE_RATE, RANGE_PCT)
        crossings = gf.find_flip_point(price_grid, gex_values)
        current_gex = float(np.interp(spot, price_grid, gex_values))
        row["mode"] = "black76_scan"
        row["net_gex"] = round(current_gex, 0)
        row["regime"] = "포지티브 감마" if current_gex > 0 else "네거티브 감마"
        if crossings:
            nearest = min(crossings, key=lambda x: abs(x - spot))
            row["gamma_flip_level"] = round(nearest, 2)
            row["flip_distance_pt"] = round(nearest - spot, 1)
            row["flip_distance_pct"] = round((nearest - spot) / spot * 100, 2)
    elif n_gamma > 0:
        current_gex, n_c, n_p = gf.compute_current_gex_from_barchart_gamma(chain, spot, multiplier)
        row["mode"] = "barchart_gamma"
        row["net_gex"] = round(current_gex, 0)
        row["regime"] = "포지티브 감마" if current_gex > 0 else "네거티브 감마"
    else:
        row["mode"] = "none"

    walls = gf.find_walls_futures_raw(chain)
    walls_sm = gf.find_walls_futures_smoothed(chain, spot, WALL_BANDWIDTH_PCT)
    if "call_wall_strike" in walls:
        row["call_wall"] = round(walls["call_wall_strike"], 2)
        row["call_wall_oi"] = int(walls["call_wall_oi"])
    if "put_wall_strike" in walls:
        row["put_wall"] = round(walls["put_wall_strike"], 2)
        row["put_wall_oi"] = int(walls["put_wall_oi"])
    if "call_wall_strike" in walls_sm:
        row["call_wall_smoothed"] = round(walls_sm["call_wall_strike"], 2)
        row["call_wall_smoothed_oi"] = round(walls_sm["call_wall_region_oi"], 0)
    if "put_wall_strike" in walls_sm:
        row["put_wall_smoothed"] = round(walls_sm["put_wall_strike"], 2)
        row["put_wall_smoothed_oi"] = round(walls_sm["put_wall_region_oi"], 0)

    return row


def append_history(symbol: str, row: dict):
    """symbol 전용 히스토리 파일(HISTORY_PATHS[symbol])에 오늘자 행 1개를 추가한다.
    같은 날짜(date_kst) 행이 이미 있으면 이번에 새로 계산한 값으로 덮어쓴다 —
    수동 재실행(workflow_dispatch)으로 하루에 여러 번 돌아도 하루당 한 행만
    남는다. keep="last"라 새로 append된 쪽(이번 실행)이 이긴다."""
    history_path = HISTORY_PATHS[symbol]
    new_df = pd.DataFrame([row], columns=HISTORY_COLUMNS)
    if os.path.exists(history_path):
        old_df = pd.read_csv(history_path)
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["date_kst"], keep="last")
        combined = combined.sort_values(["date_kst"]).reset_index(drop=True)
    else:
        combined = new_df
    combined.to_csv(history_path, index=False)
    return history_path


def save_dated_archive(now_kst: datetime) -> str:
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    df["download_date_kst"] = now_kst.strftime("%Y-%m-%d")
    df["download_datetime_kst"] = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    dated_path = os.path.join(ARCHIVE_DIR, f"barchart_options_capture_{now_kst.strftime('%Y-%m-%d')}.csv")
    df.to_csv(dated_path, index=False)
    return dated_path


def main():
    now_kst = datetime.now(KST)

    print(f"[1/3] NQ/ES 캡처 중 (Playwright, ubuntu-latest — glibc 낮은 서버 우회용)...")
    gf.run_capture_sync(SYMBOLS, CSV_PATH)

    if not os.path.exists(CSV_PATH):
        sys.exit("캡처 실패: CSV 파일이 생성되지 않았습니다. 위 [경고]/[오류] 로그를 확인하세요.")

    now_epoch = time.time()
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "captured_at_epoch": now_epoch,
            "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_epoch)),
        }, f)

    print(f"[2/3] 날짜별 보관 파일 저장 중 (KST {now_kst.strftime('%Y-%m-%d %H:%M:%S')})...")
    dated_path = save_dated_archive(now_kst)
    print(f"      -> {dated_path}")

    print("[3/3] 감마 플립/콜월/풋월 계산 후 심볼별 히스토리 CSV에 기록 중...")
    for symbol in SYMBOLS:
        try:
            row = summarize_symbol(symbol, now_kst)
            history_path = append_history(symbol, row)
            print(f"      {symbol}: spot={row['spot']}  mode={row['mode']}  "
                  f"net_gex={row['net_gex']}  regime={row['regime']}  "
                  f"flip={row['gamma_flip_level']}  -> {history_path}")
        except Exception as e:
            print(f"  [경고] {symbol} 분석 실패, 히스토리에 기록하지 않습니다: {type(e).__name__}: {e}")

    print("\n완료. git 커밋/푸시는 워크플로(capture.yml)에서 이어집니다.")


if __name__ == "__main__":
    main()
