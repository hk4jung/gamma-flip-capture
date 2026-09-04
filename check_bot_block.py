#!/usr/bin/env python3
"""진단 전용: Barchart가 이 실행 환경(예: GitHub Actions의 데이터센터 IP)을
봇으로 차단/의심하고 있는지 확인한다.

확인하는 것:
  1) 메인 문서 요청의 HTTP 상태 코드 (403/429/503 등이면 명백한 차단 신호)
  2) 응답 헤더에 알려진 봇 차단 업체(Cloudflare/Akamai/PerimeterX(HUMAN)/DataDome
     등)의 흔적이 있는지 (특정 헤더 이름, 특정 쿠키 이름)
  3) 페이지 본문에 "챌린지 페이지" 특유의 문구("Just a moment", "Access Denied",
     "unusual traffic", "verify you are human" 등)가 있는지
  4) 실제로 눈으로 보기 위한 스크린샷 (GitHub Actions 아티팩트로 다운로드해서
     확인 — 로그에는 이미지가 안 나오니 이게 제일 확실함)

정상적인(차단 아닌) 페이지라면 이 문구들이 하나도 안 나오고, 상태 코드는
200이며, 스크린샷에는 실제 옵션 시세/그릭스 표가 보여야 한다."""
import asyncio
import sys
from playwright.async_api import async_playwright

TARGETS_TO_CHECK = [
    ("옵션 프라이스 페이지", "https://www.barchart.com/futures/quotes/NQU26/options/MQ1U26"
                          "?moneyness=allRows&futuresOptionsView=merged"),
    ("Volatility & Greeks 페이지", "https://www.barchart.com/futures/quotes/NQU26/volatility-greeks"
                                  "?moneyness=allRows&futuresOptionsView=merged"),
]

# 알려진 봇 차단/챌린지 서비스의 흔적들. 헤더 이름은 소문자로 비교한다.
BOT_HEADER_SIGNATURES = [
    "cf-mitigated", "cf-ray", "x-datadome", "x-px", "x-perimeterx",
    "x-akamai-transformed", "x-sucuri-id", "server-timing",
]
BOT_COOKIE_SIGNATURES = ["__cf_bm", "_px", "_px2", "_px3", "datadome", "perimeterx", "incap_ses", "visid_incap"]
BOT_BODY_PHRASES = [
    "just a moment", "checking your browser", "access denied",
    "unusual traffic", "verify you are human", "are you a robot",
    "please enable javascript and cookies", "captcha", "attention required",
    "sorry, you have been blocked", "request unsuccessful",
]


async def check(label: str, url: str, idx: int):
    print(f"\n{'=' * 70}\n[{label}]\n{url}\n{'=' * 70}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"[결과] 페이지 로드 자체가 실패함: {e}")
            await browser.close()
            return

        status = resp.status if resp else None
        headers = {k.lower(): v for k, v in (resp.headers if resp else {}).items()}
        print(f"[1] HTTP 상태 코드: {status}"
              + ("  <- 403/429/503이면 명백한 차단 신호" if status and status >= 400 else ""))

        hit_headers = [h for h in BOT_HEADER_SIGNATURES if h in headers]
        print(f"[2] 응답 헤더 목록: {sorted(headers.keys())}")
        print(f"    봇 차단 업체 관련 헤더 발견: {hit_headers if hit_headers else '없음'}")

        cookies = await page.context.cookies()
        cookie_names = [c["name"] for c in cookies]
        hit_cookies = [c for c in cookie_names if any(sig in c.lower() for sig in BOT_COOKIE_SIGNATURES)]
        print(f"[3] 쿠키 이름 목록: {cookie_names}")
        print(f"    봇 차단 업체 관련 쿠키 발견: {hit_cookies if hit_cookies else '없음'}")

        await page.wait_for_timeout(3000)  # 챌린지가 있다면 렌더링될 시간을 줌
        body_text = (await page.inner_text("body"))[:3000].lower()
        hit_phrases = [p for p in BOT_BODY_PHRASES if p in body_text]
        print(f"[4] 챌린지 페이지 문구 발견: {hit_phrases if hit_phrases else '없음'}")
        print(f"    본문 앞부분 미리보기: {body_text[:200]!r}")

        screenshot_path = f"botcheck_{idx}.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"[5] 스크린샷 저장: {screenshot_path} (워크플로우 아티팩트로 다운로드해서 눈으로 확인)")

        # 종합 판정 (참고용 — 최종 판단은 스크린샷을 직접 보고 하는 게 가장 정확함)
        suspicious = bool(hit_headers or hit_cookies or hit_phrases or (status and status >= 400))
        print(f"\n[종합 판정] {'봇 차단/챌린지 의심됨' if suspicious else '차단 흔적 없음 (정상 페이지로 보임)'}")

        await browser.close()


async def main():
    for i, (label, url) in enumerate(TARGETS_TO_CHECK, 1):
        await check(label, url, i)


if __name__ == "__main__":
    asyncio.run(main())
