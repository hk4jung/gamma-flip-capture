#!/usr/bin/env python3
"""진단 전용 스크립트: "Volatility & Greeks" 페이지(/options가 아니라
/volatility-greeks)를 캡처했을 때 impliedVolatility/delta/gamma 등이
실제로 채워지는지 확인한다. GAMMA_FLIP_DEBUG=1로 실행하면 캡처 중
가로챈 실제 API 호출 URL과 필드 목록까지 로그에 그대로 찍힌다.

운영 캡처(capture_and_publish.py, TARGETS)에는 영향 없음 — 이 스크립트는
독립적으로 실행되는 진단용이다."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamma_flip as gf  # noqa: E402
from playwright.async_api import async_playwright


async def check(label, url):
    print(f"\n{'=' * 70}\n[{label}] {url}\n{'=' * 70}")
    cfg = {"url": url, "multiplier": 20.0}
    df = await gf.capture_one("NQ", cfg, async_playwright)
    print(f"행 수: {len(df)}")
    if len(df) == 0:
        print("데이터 없음 — 이 URL/페이지 구조로는 캡처 실패")
        return
    print(f"컬럼 목록: {df.columns.tolist()}")
    if "impliedVolatility" in df.columns:
        n_iv = df["impliedVolatility"].notna().sum()
        print(f"IV 있는 행: {n_iv} / {len(df)}")
        if n_iv > 0:
            print(df[["strike", "type", "impliedVolatility"]].dropna(subset=["impliedVolatility"]).head(10).to_string())
    else:
        print("impliedVolatility 컬럼 자체가 없음")


async def main():
    await check("옵션 프라이스 페이지 (기존)",
                "https://www.barchart.com/futures/quotes/NQU26/options/MQ1U26"
                "?moneyness=allRows&futuresOptionsView=merged")
    await check("Volatility & Greeks 페이지 (접미사 없음)",
                "https://www.barchart.com/futures/quotes/NQU26/volatility-greeks"
                "?moneyness=allRows&futuresOptionsView=merged")
    await check("Volatility & Greeks 페이지 (MQ1U26 접미사)",
                "https://www.barchart.com/futures/quotes/NQU26/volatility-greeks/MQ1U26"
                "?moneyness=allRows&futuresOptionsView=merged")


if __name__ == "__main__":
    asyncio.run(main())
