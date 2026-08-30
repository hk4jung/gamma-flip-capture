"""
gamma_flip.py
=============
SPY(또는 다른 옵션 유동성이 충분한 ETF/지수) 옵션체인을 이용해
딜러 감마 익스포저(GEX)를 추정하고 감마 플립(Zero Gamma) 레벨을 계산합니다.

데이터 소스: Yahoo Finance (yfinance) - 무료, 약간의 지연 있음.
* 지수 옵션(SPX)은 yfinance로 직접 못 가져오므로 SPY(SPX의 1/10 트래킹 ETF)를 기본값으로 사용합니다.
* SPY 기준 플립 레벨에 10을 곱하면 대략적인 SPX 환산값이 됩니다 (완전히 정확하지는 않음).

방법론 (업계에서 흔히 쓰이는 단순화된 GEX 계산 방식):
1. 만기별 콜/풋 옵션체인에서 오픈인터레스트(OI)와 내재변동성(IV)을 가져온다.
2. 여러 개의 가상 기초자산 가격(spot 후보군)에 대해 Black-Scholes 감마를 각 옵션마다 재계산한다.
   (감마는 spot에 따라 달라지므로, "플립 지점"을 찾으려면 spot을 바꿔가며 감마를 다시 계산해야 한다.)
3. 딜러 포지셔닝 관례(다수의 공개 GEX 계산기가 쓰는 표준 가정):
      - 콜 매수 주문이 많다고 가정 -> 딜러는 콜에 대해 매도(숏) 포지션 -> 콜 감마는 딜러 기준 (+)로 집계
      - 풋 매수 주문이 많다고 가정 -> 딜러는 풋에 대해 매수(롱) 포지션 -> 풋 감마는 딜러 기준 (-)로 집계
   즉: GEX(spot) = Σ [ CallGamma(spot)*CallOI - PutGamma(spot)*PutOI ] * 100 * spot^2 * 0.01
   ※ 이는 실제 딜러 포지션을 알 수 없는 상태에서의 표준적 근사치이며, 실제와 다를 수 있습니다.
4. GEX(spot) 곡선이 양수에서 음수로 바뀌는 지점(0을 교차하는 지점)이 감마 플립 레벨이다.

콜월 / 풋월 (Call Wall / Put Wall):
플립 레벨과는 별개의 계산입니다. 플립은 콜-풋을 "순계산"해서 0이 되는 지점을 찾는 것이고,
콜월/풋월은 콜과 풋을 각각 따로 보고 오픈인터레스트가 가장 많이 쌓인 행사가를 찾는 것입니다.
   콜월 = 해당 만기에서 콜 OI가 가장 큰 행사가 (다수 GEX 서비스가 쓰는 정의)
   풋월 = 해당 만기에서 풋 OI가 가장 큰 행사가
계약이 많이 몰린 행사가일수록 그 근처의 딜러 헤지 물량도 커지기 때문에, 콜월은 저항으로,
풋월은 지지로 작용하는 경향이 있다고 해석됩니다. 다만 이것도 "경향"이지 확정적 신호는 아닙니다.
※ 벤더에 따라 순수 OI가 아니라 달러 감마(OI×감마×승수×spot²)로 가중해서 벽을 뽑기도 합니다.
   이 스크립트는 가장 널리 쓰이는 정의인 순수 OI 기준을 채택했습니다.

사용법:
    python3 gamma_flip.py                 # 기본값: SPY, 만기 45일 이내
    python3 gamma_flip.py --ticker QQQ    # 나스닥100(QQQ) 기준
    python3 gamma_flip.py --ticker SPY --max-days 30

NQ=F / ES=F (CME 선물옵션) 지원 — Barchart 캡처까지 이 파일 하나로 통합됨:
    python3 gamma_flip.py --ticker NQ=F
    python3 gamma_flip.py --ticker ES=F --futures-csv barchart_options_capture.csv
    python3 gamma_flip.py --ticker NQ=F --recapture        # CSV가 있어도 강제로 새로 캡처
    python3 gamma_flip.py --ticker NQ=F --capture-both      # NQ/ES 둘 다 한 번에 캡처

    ⚠️ 중요: yfinance는 CME 선물옵션 체인 자체를 지원하지 않습니다(NQ=F/ES=F로
    가격은 가져와도 .option_chain()은 안 됨). 그래서 --ticker가 NQ, NQ=F, ES,
    ES=F 중 하나면 yfinance를 아예 호출하지 않고 대신:
      1) barchart_options_capture.csv가 이미 있으면 그걸 바로 읽어서 분석합니다.
      2) 없으면(또는 --recapture를 주면) Barchart에서 직접 캡처한 뒤, 그 결과로
         바로 분석까지 이어서 합니다 — 두 스크립트를 따로 돌릴 필요 없이 이 파일
         하나로 끝납니다.
    캡처는 기본적으로 requests만으로(브라우저 불필요) 이루어집니다 — Barchart
    옵션 페이지의 csrf_token/XSRF-TOKEN이 페이지 최초 응답에 정적으로 실려 오는
    값이라 브라우저로 JS를 실행하지 않아도 얻을 수 있다는 게 실서버(2026-08,
    구형 Ubuntu라 Chromium이 아예 못 뜨는 환경)에서 확인됐습니다. requests 방식이
    실패하는 심볼에 한해서만, playwright가 설치돼 있으면 자동으로 그쪽으로
    재시도합니다(설치: pip install playwright && playwright install --with-deps
    chromium) — 즉 playwright는 이제 필수가 아니라 선택적 보험입니다.
    Barchart 이용약관상 자동 스크래핑은 비정기적·개인적 용도로만 쓰시길
    권장하며, 반복적/공개적 사용 시 IP가 차단될 수 있습니다.
    (참고: "ES"는 실제로 Eversource Energy라는 뉴욕증권거래소 상장 유틸리티
    회사의 진짜 티커라서, 이 분기 처리 없이 yfinance로 그냥 --ticker ES를
    돌리면 에러 없이 엉뚱한 회사 옵션 데이터가 나오는 함정이 있었습니다.)

NQ=F/ES=F의 감마 플립 "가격 레벨" 계산 (Black-76 delta 역산):
    Barchart는 옵션별 impliedVolatility를 거의 항상 N/A로 내려주기 때문에(구독
    필요 추정), 가상 spot을 스캔해서 플립 가격을 찾으려면 IV가 필요한데 그게
    없다는 게 오랫동안 막혀 있던 문제였습니다. 대신 Barchart는 delta는 내려주므로,
    이 delta로부터 Black-76(선물옵션 표준 모델) 공식을 역으로 풀어 IV를 추정합니다.
      - ITM 옵션은 Black-76 델타가 sigma에 대해 비단조(U자형)라서 같은 delta를
        만드는 sigma가 2개 이상 나올 수 있습니다. 그리드 스캔으로 모든 근을 찾은 뒤
        "가장 작은 sigma"를 채택합니다 — 실제 캡처 데이터로 검증한 결과, spot 근처
        strike들과 부드럽게 이어지는 현실적인 해는 항상 작은 쪽이었고, 큰 쪽은
        수치적으로는 맞지만 (수백~수천%의 비현실적인 변동성) 경제적으로 스퓨리어스한
        해였습니다.
      - 이렇게 역산한 IV(iv_effective, iv_source="delta")는 실제 IV(iv_source="real")가
        있으면 그걸 우선 쓰고, 없을 때만 보조로 사용합니다.
      - 역산까지 포함해도 유효 IV가 --futures-min-iv-rows 미만이면 모드 B(Barchart
        자체 gamma로 "현재 레짐"만 판단, 가격 레벨은 계산 불가)로 자동 전환됩니다.
"""

import argparse
import asyncio
import html as html_module  # 이름 충돌 방지: 캡처 로직 곳곳에서 지역변수 이름으로 html(문자열)을 쓰기 때문
import io
import json
import os
import re
import sys
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

try:
    import yfinance as yf
except ImportError:
    sys.exit("yfdb가 필요합니다: pip install yfinance")

try:
    import requests
except ImportError:
    sys.exit("requests가 필요합니다: pip install requests")

# ---------------------------------------------------------------
# [디버그] 태그 붙은 상세 로그 on/off 스위치. 기본은 꺼짐(조용한 출력) —
# 웹 서비스에서 결과 화면에 캡처 내부 동작 로그까지 다 보이는 걸 막기 위함.
# 켜려면: 환경변수 GAMMA_FLIP_DEBUG=1, 또는 CLI에 --debug.
# ---------------------------------------------------------------
DEBUG_VERBOSE = os.environ.get("GAMMA_FLIP_DEBUG", "0") == "1"


def dprint(*args, **kwargs):
    if DEBUG_VERBOSE:
        print(*args, **kwargs)


# ---------------------------------------------------------------
# NQ=F / ES=F 처리용 설정. --ticker가 이 중 하나(대소문자 무관)로 들어오면
# yfinance를 건너뛰고 Barchart CSV 기반 경로로 전환한다.
# ---------------------------------------------------------------
FUTURES_TICKER_ALIASES = {
    "NQ": "NQ", "NQ=F": "NQ",
    "ES": "ES", "ES=F": "ES",
}
FUTURES_CSV_DEFAULT = "barchart_options_capture.csv"
FUTURES_MIN_IV_ROWS_DEFAULT = 5
FUTURES_WALL_BANDWIDTH_PCT_DEFAULT = 0.01

# ---------------------------------------------------------------
# Barchart 캡처 대상. 예전에는 URL에 만기 코드를 직접 박아뒀는데(NQU26,
# MQ1U26 등), 근월 선물이 롤될 때마다(예: U26 9월물 -> Z26 12월물) 사람이
# 수동으로 갱신해야 하는 문제가 있었다.
#
# 실제로는 그럴 필요가 없다: capture_one_requests()/capture_one()이 페이지를
# 연 뒤 실제 API 심볼은 그 HTML 안의 data-api-config(우선) 또는 bc_ticker
# 메타값에서 매번 새로 읽어온다(extract_api_symbol_from_config, extract_page_meta
# 참고) — 즉 cfg["url"]은 "어느 페이지를 열지"만 정할 뿐, 거기 박힌 심볼 문자열
# 자체가 실제 API 호출에 쓰이는 게 아니다. 그래서 Barchart가 제공하는 "최근월물"
# 별칭인 NQ*0/ES*0을 대신 쓰면, 페이지 자체가 그 시점의 실제 최근월 계약으로
# 서버사이드에서 렌더링돼서 내려오고(2026-08-26 확인: NQ*0/options가 그 순간의
# NQU26 9월물 데이터를 실시간으로 그대로 보여줌), data-api-config/bc_ticker도
# 그 실제 계약의 진짜 심볼로 채워져 있다. 결과적으로 만기가 롤돼도 이 URL을
# 손댈 필요가 없다 — Barchart가 알아서 다음 근월물로 넘겨준다.
#
# 혹시 나중에 Barchart가 "*0" 별칭 처리 방식을 바꿔서 이게 더 이상 안 풀리면
# (즉 실제 계약이 아니라 "*0"이 그대로 남은 문자열이 온다면) capture_one_requests()
# 쪽에 넣어둔 경고 로그("확인 필요: 심볼에 '*' 포함")가 찍히니 그때 다시
# 만기 코드를 직접 박는 예전 방식으로 되돌리면 된다.
# ---------------------------------------------------------------
TARGETS = {
    "NQ": {"url": "https://www.barchart.com/futures/quotes/NQ*0/options"
                  "?moneyness=allRows&futuresOptionsView=merged", "multiplier": 20.0},
    "ES": {"url": "https://www.barchart.com/futures/quotes/ES*0/options"
                  "?moneyness=allRows&futuresOptionsView=merged", "multiplier": 50.0},
}
# "Volatility & Greeks" 페이지 — 옵션 프라이스 페이지(TARGETS)와 다른 뷰라 별도 URL.
# 2026-08 말경 옵션 프라이스 페이지가 더 이상 IV/그릭스를 안 내려주는 게 확인돼서
# (openInterest 등은 그대로 나옴) 이 페이지에서 그릭스만 따로 캡처해 병합한다.
TARGETS_GREEKS = {
    "NQ": {"url": "https://www.barchart.com/futures/quotes/NQ*0/volatility-greeks"
                  "?moneyness=allRows&futuresOptionsView=merged"},
    "ES": {"url": "https://www.barchart.com/futures/quotes/ES*0/volatility-greeks"
                  "?moneyness=allRows&futuresOptionsView=merged"},
}
MANUAL_OVERRIDE = {}  # 예: MANUAL_OVERRIDE["NQ"] = {"spot": 25400.0, "expiration": "2026-09-19"}
MAX_BODY_BYTES = 5_000_000
CAPTURE_API_URL = "https://www.barchart.com/proxies/core-api/v1/quotes/get"
CAPTURE_API_FIELDS = (
    "strike,openPrice,highPrice,lowPrice,lastPrice,priceChange,bidPrice,askPrice,"
    "volume,openInterest,premium,tradeTime,longSymbol,optionType,symbol,"
    "impliedVolatility,delta,gamma,theta,vega,rho,expirationDate,daysToExpiration"
)
FUTURES_CSV_COLUMNS = ["symbol", "strike", "type", "openInterest", "impliedVolatility",
                        "delta_barchart", "gamma_barchart", "theta_barchart", "vega_barchart",
                        "expiration", "spot", "contract_multiplier"]


def bs_gamma(S, K, T, sigma, r=0.05):
    """Black-Scholes 감마 (콜/풋 동일)."""
    S = np.asarray(S, dtype=float)
    T = np.maximum(np.asarray(T, dtype=float), 1e-6)
    sigma = np.maximum(np.asarray(sigma, dtype=float), 1e-4)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    return gamma


def b76_delta(F, K, T, sigma, r, opt_type: str):
    """Black-76 델타 (선물옵션 표준 모델). opt_type: 'call' 또는 'put'."""
    F = np.asarray(F, dtype=float)
    T = max(float(T), 1e-6)
    sigma = max(float(sigma), 1e-6)
    d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / (sigma * np.sqrt(T))
    disc = np.exp(-r * T)
    return disc * norm.cdf(d1) if opt_type == "call" else -disc * norm.cdf(-d1)


def b76_gamma(F, K, T, sigma, r=0.04):
    """Black-76 감마 (콜/풋 동일, 선물옵션용). ETF 경로의 bs_gamma와 달리 배당/드리프트 항이 없다."""
    F = np.asarray(F, dtype=float)
    T = np.maximum(np.asarray(T, dtype=float), 1e-6)
    sigma = np.maximum(np.asarray(sigma, dtype=float), 1e-4)
    d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / (sigma * np.sqrt(T))
    disc = np.exp(-r * T)
    return disc * norm.pdf(d1) / (F * sigma * np.sqrt(T))


def solve_iv_roots_from_delta_b76(delta, F, K, T, r, opt_type: str, sigma_grid=None):
    """delta를 만족하는 Black-76 sigma 근을 "전부" 찾아 오름차순 리스트로 반환.

    왜 근이 여러 개인가 (수학적 배경):
        d1 = ln(F/K)/(σ√T) + (σ√T)/2 이므로, m = ln(F/K) > 0 (즉 K < F)이면
        d1은 σ√T = √(2m)에서 최솟값을 갖는 U자 곡선이 된다. delta는 d1의 단조
        함수이므로 delta(σ)도 U자형이 되고, 하나의 delta 값에 sigma 근이 2개
        생긴다. 분기점은 σ* = √(2m/T).
        반대로 K >= F (m <= 0)이면 d1이 σ에 대해 단조증가라 근이 유일하다.

    즉 "K < F인 행은 delta만으로 IV가 유일하게 결정되지 않는다"는 게 데이터의
    본질적 한계다. 어느 근이 맞는지는 여기가 아니라 호출부에서 스마일 연속성
    같은 추가 정보로 골라야 한다.
    """
    if sigma_grid is None:
        sigma_grid = np.linspace(0.005, 3.0, 1200)
    # b76_delta는 sigma를 스칼라로 강제해서 그리드 전체를 넘기면 안 되므로, 여기서는
    # b76_delta와 동일한 공식을 sigma_grid 전체에 대해 numpy로 한 번에 계산한다.
    # (예전엔 1200개 그리드 포인트마다 파이썬 루프로 b76_delta를 개별 호출했는데,
    # 느린 CPU에서는 이게 체감될 만큼 오래 걸려서 벡터화함 — 결과값은 동일)
    T_ = max(float(T), 1e-6)
    d1_grid = (np.log(F / K) + 0.5 * sigma_grid ** 2 * T_) / (sigma_grid * np.sqrt(T_))
    disc = np.exp(-r * T_)
    delta_grid = disc * norm.cdf(d1_grid) if opt_type == "call" else -disc * norm.cdf(-d1_grid)
    resid = delta_grid - delta
    absresid = np.abs(resid)
    roots = []
    for i in range(1, len(sigma_grid) - 1):
        if absresid[i] < absresid[i - 1] and absresid[i] <= absresid[i + 1] and absresid[i] < 1e-3:
            lo, hi = sigma_grid[i - 1], sigma_grid[i + 1]
            try:
                if resid[i - 1] * resid[i + 1] < 0:
                    root = brentq(lambda s: b76_delta(F, K, T, s, r, opt_type) - delta, lo, hi, xtol=1e-10)
                else:
                    root = sigma_grid[i]
            except Exception:
                root = sigma_grid[i]
            if abs(b76_delta(F, K, T, root, r, opt_type) - delta) <= 1e-3 and 0.02 <= root <= 2.0:
                roots.append(root)
    roots = sorted(roots)
    deduped = []
    for x in roots:  # 수치적으로 거의 겹치는 근은 하나로 합침
        if not deduped or abs(x - deduped[-1]) > 1e-4:
            deduped.append(x)
    return deduped


def implied_vol_from_delta_b76(delta, F, K, T, r, opt_type: str, reference_iv=None, sigma_grid=None):
    """delta로부터 Black-76 IV 역산. 근이 여러 개면 reference_iv에 가장 가까운 근을 고른다.

    reference_iv를 안 주면 최소근을 고르는데, 이는 K가 F 바로 아래일 때
    (σ* = √(2·ln(F/K)/T)가 작아지는 구간) 틀린 근을 고를 수 있다. 그래서 실제
    파이프라인(derive_effective_iv_futures)은 항상 reference_iv를 넘겨준다.
    반환: (sigma, residual) 또는 (None, None).
    """
    roots = solve_iv_roots_from_delta_b76(delta, F, K, T, r, opt_type, sigma_grid)
    if not roots:
        return None, None
    if reference_iv is not None and np.isfinite(reference_iv):
        best = min(roots, key=lambda s: abs(s - reference_iv))
    else:
        best = roots[0]
    return best, abs(b76_delta(F, K, T, best, r, opt_type) - delta)


def _fit_reference_smile(anchors):
    """앵커 [(ln(K/F), iv), ...]로 IV ≈ a + b·ln(K/F) 선형 스마일을 적합해서,
    모호한 strike에서 어느 근이 맞는지 고를 기준값 함수를 만든다. 두 근은 보통
    크게 떨어져 있어(예: 0.15 vs 0.21, 0.21 vs 2.5) 기준값이 대략만 맞아도 된다."""
    if len(anchors) >= 3:
        xs = np.array([a[0] for a in anchors])
        ys = np.array([a[1] for a in anchors])
        b, a = np.polyfit(xs, ys, 1)
        return lambda lm: float(np.clip(a + b * lm, 0.02, 2.0))
    if anchors:
        med = float(np.median([a[1] for a in anchors]))
        return lambda lm: med
    return None


def derive_effective_iv_futures(chain: pd.DataFrame, spot: float, r: float = 0.04) -> pd.DataFrame:
    """각 행에 iv_effective(쓸 IV)와 iv_source를 채운다.

    2패스인 이유: delta→IV 역산은 K < spot인 행에서 근이 2개 나와 유일하지 않다
    (solve_iv_roots_from_delta_b76 설명 참고). 그래서
      1패스 — 근이 유일한 행(K >= spot 등)만 먼저 풀어 "믿을 수 있는 앵커"로 삼고
              그걸로 스마일을 적합한다.
      2패스 — 모호한 행은 그 스마일 기준값에 가장 가까운 근을 고른다.
    무조건 최소근을 고르면 spot 바로 아래 strike(=감마 기여가 가장 큰 ATM 구간!)
    에서 체계적으로 낮은 IV가 찍히는 버그가 생긴다. 실제로 K=29800(spot 29834.75)
    에서 이웃이 0.205인데 0.15가 찍히던 것을 이 구조로 잡았다.
    iv_source: real / delta_unique(유일근) / delta_smile(스마일로 근 선택) / none"""
    chain = chain.copy()
    n = len(chain)
    iv_eff = [np.nan] * n
    iv_src = ["none"] * n
    roots_cache = {}

    # ---- 1패스: 유일근(앵커) 확보 ----
    anchors = []
    for pos in range(n):
        row = chain.iloc[pos]
        real_iv = row.get("impliedVolatility")
        if pd.notna(real_iv) and real_iv > 0:
            iv_eff[pos] = float(real_iv)
            iv_src[pos] = "real"
            anchors.append((np.log(float(row["strike"]) / spot), float(real_iv)))
            continue
        delta = row.get("delta_barchart")
        if pd.isna(delta) or pd.isna(row.get("T")):
            continue
        roots = solve_iv_roots_from_delta_b76(float(delta), spot, float(row["strike"]),
                                               float(row["T"]), r, row["type"])
        roots_cache[pos] = roots
        if len(roots) == 1:
            iv_eff[pos] = roots[0]
            iv_src[pos] = "delta_unique"
            anchors.append((np.log(float(row["strike"]) / spot), roots[0]))

    # ---- 2패스: 모호한 행은 스마일 기준값에 가장 가까운 근 선택 ----
    ref_fn = _fit_reference_smile(anchors)
    for pos, roots in roots_cache.items():
        if iv_src[pos] != "none" or not roots:
            continue
        lm = np.log(float(chain.iloc[pos]["strike"]) / spot)
        iv_eff[pos] = roots[0] if ref_fn is None else min(roots, key=lambda s: abs(s - ref_fn(lm)))
        iv_src[pos] = "delta_smile"

    chain["iv_effective"] = iv_eff
    chain["iv_source"] = iv_src
    return chain


def fetch_chain(ticker: str, max_days: int) -> pd.DataFrame:
    tk = yf.Ticker(ticker)
    spot = tk.history(period="1d")["Close"].iloc[-1]

    expirations = tk.options
    if not expirations:
        sys.exit(f"{ticker}에 대한 옵션 만기 정보를 가져오지 못했습니다.")

    today = datetime.now(timezone.utc).date()
    rows = []
    for exp in expirations:
        exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
        days = (exp_date - today).days
        if days < 0 or days > max_days:
            continue
        try:
            chain = tk.option_chain(exp)
        except Exception as e:
            print(f"  [경고] {exp} 만기 데이터 로드 실패: {e}", file=sys.stderr)
            continue

        T = max(days, 1) / 365.0

        calls = chain.calls.copy()
        calls["type"] = "call"
        puts = chain.puts.copy()
        puts["type"] = "put"

        for df in (calls, puts):
            df["expiration"] = exp
            df["T"] = T

        rows.append(calls)
        rows.append(puts)

    if not rows:
        sys.exit(f"{max_days}일 이내 만기 옵션 데이터가 없습니다. --max-days 값을 늘려보세요.")

    full = pd.concat(rows, ignore_index=True)
    full = full[["strike", "type", "openInterest", "impliedVolatility", "T", "expiration"]]
    full = full.dropna(subset=["strike", "openInterest", "impliedVolatility"])
    full = full[(full["openInterest"] > 0) & (full["impliedVolatility"] > 0)]
    return full, float(spot)


def compute_gex_curve(chain: pd.DataFrame, spot: float, price_range_pct: float = 0.15, n_points: int = 121):
    calls = chain[chain["type"] == "call"]
    puts = chain[chain["type"] == "put"]

    price_grid = np.linspace(spot * (1 - price_range_pct), spot * (1 + price_range_pct), n_points)

    gex_values = []
    for S in price_grid:
        call_gamma = bs_gamma(S, calls["strike"].values, calls["T"].values, calls["impliedVolatility"].values)
        put_gamma = bs_gamma(S, puts["strike"].values, puts["T"].values, puts["impliedVolatility"].values)

        call_gex = np.sum(call_gamma * calls["openInterest"].values) * 100 * S ** 2 * 0.01
        put_gex = np.sum(put_gamma * puts["openInterest"].values) * 100 * S ** 2 * 0.01

        net_gex = call_gex - put_gex
        gex_values.append(net_gex)

    return price_grid, np.array(gex_values)


def find_walls(chain: pd.DataFrame) -> pd.DataFrame:
    """만기별로 콜월(콜 OI 최댓값 행사가)과 풋월(풋 OI 최댓값 행사가)을 찾는다."""
    rows = []
    for exp, grp in chain.groupby("expiration"):
        calls = grp[grp["type"] == "call"]
        puts = grp[grp["type"] == "put"]

        row = {"expiration": exp}
        if not calls.empty:
            top_call = calls.loc[calls["openInterest"].idxmax()]
            row["call_wall_strike"] = top_call["strike"]
            row["call_wall_oi"] = int(top_call["openInterest"])
        else:
            row["call_wall_strike"] = row["call_wall_oi"] = None

        if not puts.empty:
            top_put = puts.loc[puts["openInterest"].idxmax()]
            row["put_wall_strike"] = top_put["strike"]
            row["put_wall_oi"] = int(top_put["openInterest"])
        else:
            row["put_wall_strike"] = row["put_wall_oi"] = None

        rows.append(row)
    return pd.DataFrame(rows).sort_values("expiration").reset_index(drop=True)


def find_walls_aggregate(chain: pd.DataFrame) -> dict:
    """포함된 모든 만기를 합산했을 때(=현재 화면에 걸린 전체 옵션 기준) 콜월/풋월."""
    calls = chain[chain["type"] == "call"].groupby("strike")["openInterest"].sum()
    puts = chain[chain["type"] == "put"].groupby("strike")["openInterest"].sum()

    result = {}
    if not calls.empty:
        result["call_wall_strike"] = float(calls.idxmax())
        result["call_wall_oi"] = int(calls.max())
    if not puts.empty:
        result["put_wall_strike"] = float(puts.idxmax())
        result["put_wall_oi"] = int(puts.max())
    return result


def find_flip_point(price_grid, gex_values):
    """부호가 바뀌는 지점을 선형보간으로 찾는다. 여러 번 교차하면 전부 반환.
    (격자점에서 정확히 0이 되는 경우 같은 교차점이 중복 수집되던 문제가 있어
    마지막에 중복 제거 — '교차점 N개' 카운트가 부풀려지지 않도록.)"""
    sign = np.sign(gex_values)
    crossings = []
    for i in range(len(sign) - 1):
        if sign[i] == 0:
            crossings.append(price_grid[i])
        elif sign[i] != sign[i + 1]:
            x0, x1 = price_grid[i], price_grid[i + 1]
            y0, y1 = gex_values[i], gex_values[i + 1]
            crossings.append(x0 - y0 * (x1 - x0) / (y1 - y0))
    if len(price_grid) > 1:
        tol = abs(price_grid[1] - price_grid[0]) * 1e-6
        deduped = []
        for c in sorted(crossings):
            if not deduped or abs(c - deduped[-1]) > tol:
                deduped.append(c)
        return deduped
    return crossings


# =================================================================
# NQ=F / ES=F (CME 선물옵션) 경로 — gamma_flip_from_csv.py와 동일한 로직.
# yfinance가 선물옵션을 지원하지 않아서 별도로 둠 (위 함수들과 이름이 겹치지
# 않도록 futures_ 접두어를 붙였고, 계약승수가 종목마다 다르다는 점과 IV가
# Barchart에서 거의 항상 N/A로 온다는 점이 ETF 경로와의 핵심 차이).
# =================================================================

def load_futures_symbol(csv_path: str, symbol: str):
    df = pd.read_csv(csv_path)
    required = {"symbol", "strike", "type", "openInterest", "expiration", "spot", "contract_multiplier"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"CSV에 필요한 컬럼이 없습니다: {missing}. CSV 캡처 코드로 다시 캡처하세요.")
    for optional_col in ("impliedVolatility", "gamma_barchart", "delta_barchart"):
        if optional_col not in df.columns:
            df[optional_col] = np.nan

    sub = df[df["symbol"] == symbol].copy()
    if sub.empty:
        available = sorted(df["symbol"].unique())
        sys.exit(f"'{symbol}' 심볼이 CSV에 없습니다. 사용 가능한 심볼: {available}")

    if sub["spot"].isna().any() or sub["expiration"].isna().any():
        sys.exit(f"{symbol}: spot 또는 expiration 값이 비어 있습니다. "
                  f"CSV 캡처 코드의 MANUAL_OVERRIDE를 채워서 다시 캡처하세요.")

    spot = float(sub["spot"].iloc[0])
    multiplier = float(sub["contract_multiplier"].iloc[0])

    today = date.today()

    def days_to_expiry(exp_str):
        exp_date = datetime.strptime(str(exp_str), "%Y-%m-%d").date()
        return max((exp_date - today).days, 1)

    sub["T"] = sub["expiration"].apply(lambda e: days_to_expiry(e) / 365.0)
    sub = sub.dropna(subset=["strike", "openInterest"])
    sub = sub[sub["openInterest"] > 0]
    return sub, spot, multiplier


def compute_gex_curve_futures_bs(chain: pd.DataFrame, spot: float, multiplier: float, r: float,
                                  price_range_pct: float = 0.15, n_points: int = 121):
    """모드 A: 유효 IV(iv_effective — 실제 IV 또는 delta 역산 IV)가 충분할 때
    Black-76(선물옵션용)으로 가상 spot을 스캔. chain에는 derive_effective_iv_futures()가
    미리 실행되어 있어야 한다 (iv_effective 컬럼 필요)."""
    calls = chain[(chain["type"] == "call") & chain["iv_effective"].notna() & (chain["iv_effective"] > 0)]
    puts = chain[(chain["type"] == "put") & chain["iv_effective"].notna() & (chain["iv_effective"] > 0)]
    price_grid = np.linspace(spot * (1 - price_range_pct), spot * (1 + price_range_pct), n_points)

    gex_values = []
    for S in price_grid:
        call_gamma = b76_gamma(S, calls["strike"].values, calls["T"].values, calls["iv_effective"].values, r)
        put_gamma = b76_gamma(S, puts["strike"].values, puts["T"].values, puts["iv_effective"].values, r)
        call_gex = np.sum(call_gamma * calls["openInterest"].values) * multiplier * S ** 2 * 0.01
        put_gex = np.sum(put_gamma * puts["openInterest"].values) * multiplier * S ** 2 * 0.01
        gex_values.append(call_gex - put_gex)

    return price_grid, np.array(gex_values)


def compute_current_gex_from_barchart_gamma(chain: pd.DataFrame, spot: float, multiplier: float):
    """모드 B: IV가 부족할 때 Barchart가 직접 계산해 내려준 gamma로 '현재 시점' 순감마만 계산.
    (가상 spot 재계산 불가 — IV를 모르므로 스캔 곡선은 못 만듦)"""
    calls = chain[(chain["type"] == "call") & chain["gamma_barchart"].notna()]
    puts = chain[(chain["type"] == "put") & chain["gamma_barchart"].notna()]
    call_gex = np.sum(calls["gamma_barchart"].values * calls["openInterest"].values) * multiplier * spot ** 2 * 0.01
    put_gex = np.sum(puts["gamma_barchart"].values * puts["openInterest"].values) * multiplier * spot ** 2 * 0.01
    return call_gex - put_gex, len(calls), len(puts)


def find_walls_futures_raw(chain: pd.DataFrame) -> dict:
    calls = chain[chain["type"] == "call"]
    puts = chain[chain["type"] == "put"]
    result = {}
    if not calls.empty:
        top = calls.loc[calls["openInterest"].idxmax()]
        result["call_wall_strike"] = float(top["strike"])
        result["call_wall_oi"] = int(top["openInterest"])
    if not puts.empty:
        top = puts.loc[puts["openInterest"].idxmax()]
        result["put_wall_strike"] = float(top["strike"])
        result["put_wall_oi"] = int(top["openInterest"])
    return result


def find_walls_futures_smoothed(chain: pd.DataFrame, spot: float, bandwidth_pct: float = 0.01,
                                 grid_points: int = 600) -> dict:
    """가우시안 커널로 주변 strike OI를 같이 반영해 'OI가 몰린 동네'를 찾는다.
    NQ처럼 옵션이 얇은 종목에서 단일 최댓값 스파이크보다 덜 튀는 결과를 준다."""
    bandwidth = max(spot * bandwidth_pct, 1e-6)
    result = {}
    for opt_type, prefix in (("call", "call"), ("put", "put")):
        sub = chain[chain["type"] == opt_type]
        if sub.empty:
            continue
        strikes = sub["strike"].values.astype(float)
        oi = sub["openInterest"].values.astype(float)
        lo, hi = strikes.min() - 3 * bandwidth, strikes.max() + 3 * bandwidth
        grid = np.linspace(lo, hi, grid_points)
        weights = np.exp(-0.5 * ((grid[:, None] - strikes[None, :]) / bandwidth) ** 2)
        smoothed = weights @ oi
        peak_idx = int(np.argmax(smoothed))
        peak_level = float(grid[peak_idx])
        near_mask = np.abs(strikes - peak_level) <= bandwidth
        result[f"{prefix}_wall_strike"] = peak_level
        result[f"{prefix}_wall_region_oi"] = float(oi[near_mask].sum())
    return result


# =================================================================
# Barchart 캡처 로직 (CSV 캡처 코드와 동일 — 자세한 배경/주의사항은
# 그 파일의 docstring 참고). CSV가 없을 때 이 스크립트 하나로 캡처부터 분석까지
# 끝낼 수 있도록 그대로 가져왔다. playwright는 여기서만 필요하므로 임포트를
# 지연시켜서, ETF(yfinance) 경로만 쓰는 사용자는 playwright 없이도 동작한다.
# =================================================================

# Barchart가 옵션 페이지의 data-api-config/bc_ticker에 "옵션 시리즈 심볼"
# (예: MQ1U26) 대신 그냥 "선물 자체 심볼"(예: NQU26)을 내려줄 때가 있다
# (2026-08-30 관측: 완전히 같은 NQ*0/options URL인데 실행마다 둘 중 하나가
# 뒤섞여서 옴 — Barchart 쪽 렌더링이 일관적이지 않은 것으로 보임). 후자로
# 오면 그 상태로 API를 불러도 옵션 체인이 아니라 선물 시세만 오거나 아예
# 빈 데이터가 온다. 다행히 둘의 관계는 고정돼 있다: 만기 코드(예: "U26")는
# 그대로고, 앞자리 루트만 규칙대로 바뀐다.
MONTHLY_OPTIONS_ROOT = {"NQ": "MQ1", "ES": "MW1"}


def normalize_options_symbol(symbol: str, ticker: str | None) -> str | None:
    """ticker가 선물 자체 심볼(예: NQU26)이면 월간 옵션 시리즈 심볼(예: MQ1U26)로
    변환한다. 이미 옵션 시리즈 심볼이거나, symbol이 매핑에 없거나, ticker가
    None이면 그대로 돌려준다."""
    if not ticker:
        return ticker
    root = MONTHLY_OPTIONS_ROOT.get(symbol)
    if not root or ticker.startswith(root):
        return ticker
    if ticker.startswith(symbol) and len(ticker) > len(symbol):
        converted = root + ticker[len(symbol):]
        print(f"  [정보] {symbol}: 선물 심볼({ticker})을 옵션 시리즈 심볼({converted})로 변환")
        return converted
    return ticker


def extract_api_symbol_from_config(html: str) -> str | None:
    """월물(Monthly) 페이지와 위클리 페이지는 data-api-config 안의 실제
    "api":{"symbol":...} 값이 다를 수 있다. bc_ticker 메타값보다 이 값이 더
    정확하므로 있으면 이걸 우선 쓴다."""
    for m in re.finditer(r'data-api-config="([^"]*)"', html):
        raw = html_module.unescape(m.group(1))
        try:
            cfg = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        api = cfg.get("api", {})
        if api.get("method") == "quotes" and api.get("list") == "futures.options" and api.get("symbol"):
            return api["symbol"]
    return None


async def extract_page_meta(page, html: str, symbol: str | None = None) -> dict:
    meta = {}
    ticker_from_config = extract_api_symbol_from_config(html)
    m = re.search(r'"bc_ticker"\s*:\s*"([^"]+)"', html)
    ticker_from_meta = m.group(1) if m else None
    ticker = ticker_from_config or ticker_from_meta
    if symbol:
        ticker = normalize_options_symbol(symbol, ticker)
    meta["ticker"] = ticker
    meta["ticker_source"] = "data-api-config" if ticker_from_config else ("bc_ticker" if ticker_from_meta else None)
    m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', html)
    meta["csrf_token"] = m.group(1) if m else None
    xsrf_cookie = None
    try:
        for c in await page.context.cookies():
            if c.get("name", "").upper() == "XSRF-TOKEN":
                from urllib.parse import unquote
                xsrf_cookie = unquote(c.get("value", ""))
                break
    except Exception:
        pass
    meta["xsrf_cookie"] = xsrf_cookie
    return meta


async def try_direct_api(page, referer_url: str, meta: dict, symbol: str) -> tuple:
    if not meta.get("ticker"):
        return None, "(bc_ticker를 페이지에서 못 찾아 직접 호출을 시도하지 않음)"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": referer_url,
    }
    if meta.get("csrf_token"):
        headers["X-CSRF-TOKEN"] = meta["csrf_token"]
    if meta.get("xsrf_cookie"):
        headers["X-XSRF-TOKEN"] = meta["xsrf_cookie"]
    params = {
        "symbol": meta["ticker"], "list": "futures.options", "fields": CAPTURE_API_FIELDS,
        "meta": "field.shortName,field.description,field.type",
        "groupBy": "optionType", "orderBy": "strike", "orderDir": "asc", "raw": "1",
    }
    try:
        resp = await page.request.get(CAPTURE_API_URL, params=params, headers=headers, timeout=20000)
        return resp.status, await resp.text()
    except Exception as e:
        return None, f"(요청 실패: {e})"


def guess_spot(html: str) -> float | None:
    m = re.search(r'"lastPrice"\s*:\s*"?([\d,]+\.?\d*)"?', html)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r'data-ng-non-bindable[^>]*>\s*([\d,]{3,}\.\d{2})\s*<', html)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r'Last\s*Price[^0-9]{0,20}([\d,]{3,}\.?\d{0,2})', html, re.I)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def guess_expiration(html: str) -> str | None:
    m = re.search(r'expiration on\s*(?:<[^>]*>\s*)*(\d{2})/(\d{2})/(\d{2})', html, re.I)
    if m:
        mm, dd, yy = m.groups()
        try:
            return datetime.strptime(f"20{yy}-{mm}-{dd}", "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
    m = re.search(r'([A-Z][a-z]{2}\s+\d{1,2},\s*20\d{2})', html)
    if m:
        try:
            return datetime.strptime(m.group(1), "%b %d, %Y").date().isoformat()
        except ValueError:
            pass
    return None


def _find_candidate_lists(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.extend(_find_candidate_lists(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        if obj and all(isinstance(x, dict) for x in obj):
            found.append((path, obj))
        for i, x in enumerate(obj[:50]):
            found.extend(_find_candidate_lists(x, f"{path}[{i}]"))
    return found


def _score_candidate(records) -> int:
    if not records:
        return -1
    keys = set()
    for r in records[:5]:
        keys.update(str(k).lower() for k in r.keys())
    score = 0
    if any("strike" in k for k in keys):
        score += 3
    if any(("open" in k and "int" in k) or re.search(r"\boi\b", k) for k in keys):
        score += 2
    if any(("impl" in k and "vol" in k) or re.search(r"\biv\b", k) for k in keys):
        score += 2
    if any("call" in k for k in keys) or any("put" in k for k in keys):
        score += 1
    return score


def _to_float(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "" or s.upper() in ("NONE", "NULL", "-", "N/A", "NA"):
        return None
    s = s.replace(",", "").replace("%", "")
    m = re.match(r"^-?\d+\.?\d*", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _get_field(d: dict, pattern: str):
    for k, v in d.items():
        if re.search(pattern, str(k), re.I):
            return v
    return None


def _normalize_iv(iv):
    if iv is None:
        return None
    return iv / 100.0 if iv > 1.5 else iv


def _build_rows_from_records(records: list) -> list:
    if not records:
        return []
    sample_keys = [str(k) for k in records[0].keys()]
    has_prefixed = (
        any(re.search(r"^call", k, re.I) for k in sample_keys)
        and any(re.search(r"^put", k, re.I) for k in sample_keys)
    )
    rows = []
    if has_prefixed:
        for r in records:
            strike = _to_float(_get_field(r, r"strike"))
            if strike is None:
                continue
            call_oi = _to_float(_get_field(r, r"call.*open.*int|call.*\boi\b"))
            call_iv = _normalize_iv(_to_float(_get_field(r, r"call.*(impl.*vol|\biv\b)")))
            put_oi = _to_float(_get_field(r, r"put.*open.*int|put.*\boi\b"))
            put_iv = _normalize_iv(_to_float(_get_field(r, r"put.*(impl.*vol|\biv\b)")))
            if call_oi is not None:
                rows.append({"strike": strike, "type": "call", "openInterest": call_oi, "impliedVolatility": call_iv})
            if put_oi is not None:
                rows.append({"strike": strike, "type": "put", "openInterest": put_oi, "impliedVolatility": put_iv})
    else:
        for r in records:
            strike = _to_float(_get_field(r, r"strike"))
            if strike is None:
                continue
            side_raw = _get_field(r, r"^(type|side|put ?call|option ?type)$")
            side = str(side_raw).lower() if side_raw is not None else ""
            opt_type = "call" if side[:1] == "c" else ("put" if side[:1] == "p" else None)
            oi = _to_float(_get_field(r, r"open.*int|\boi\b"))
            iv = _normalize_iv(_to_float(_get_field(r, r"impl.*vol|\biv\b")))
            if opt_type is not None and oi is not None:
                rows.append({"strike": strike, "type": opt_type, "openInterest": oi, "impliedVolatility": iv})
    return rows


def _find_call_put_groups(obj, path=""):
    found = []
    if isinstance(obj, dict):
        keys_lower = {str(k).lower(): k for k in obj.keys()}
        call_key = next((keys_lower[k] for k in keys_lower if k in ("call", "calls")), None)
        put_key = next((keys_lower[k] for k in keys_lower if k in ("put", "puts")), None)
        if call_key and put_key:
            call_list = obj[call_key]
            put_list = obj[put_key]
            if (isinstance(call_list, list) and call_list and all(isinstance(x, dict) for x in call_list)
                    and isinstance(put_list, list) and put_list and all(isinstance(x, dict) for x in put_list)):
                found.append((f"{path}.{{{call_key}/{put_key}}}", call_list, put_list))
        for k, v in obj.items():
            found.extend(_find_call_put_groups(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, x in enumerate(obj[:50]):
            found.extend(_find_call_put_groups(x, f"{path}[{i}]"))
    return found


def _build_rows_from_grouped(call_records: list, put_records: list) -> list:
    rows = []
    for records, opt_type in ((call_records, "call"), (put_records, "put")):
        for r in records:
            strike = _to_float(_get_field(r, r"strike"))
            if strike is None:
                continue
            oi = _to_float(_get_field(r, r"open.*int|\boi\b"))
            iv = _normalize_iv(_to_float(_get_field(r, r"impl.*vol|\biv\b")))
            delta = _to_float(_get_field(r, r"^delta$"))
            gamma = _to_float(_get_field(r, r"^gamma$"))
            theta = _to_float(_get_field(r, r"^theta$"))
            vega = _to_float(_get_field(r, r"^vega$"))
            if oi is not None:
                rows.append({
                    "strike": strike, "type": opt_type, "openInterest": oi,
                    "impliedVolatility": iv, "delta_barchart": delta, "gamma_barchart": gamma,
                    "theta_barchart": theta, "vega_barchart": vega,
                })
    return rows


def parse_from_json_candidates(captured: list) -> pd.DataFrame:
    grouped_best = None
    flat_best = None
    for url, body in captured:
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            continue
        for path, call_records, put_records in _find_call_put_groups(data):
            score = _score_candidate(call_records) + _score_candidate(put_records)
            if grouped_best is None or score > grouped_best[0]:
                grouped_best = (score, url, path, call_records, put_records)
        for path, records in _find_candidate_lists(data):
            score = _score_candidate(records)
            if score >= 5 and (flat_best is None or score > flat_best[0]):
                flat_best = (score, url, path, records)

    if grouped_best is not None:
        score, url, path, call_records, put_records = grouped_best
        dprint(f"  [디버그] Call/Put 분리 구조 채택: {url}  경로={path}  점수={score}  "
              f"콜 {len(call_records)}행 / 풋 {len(put_records)}행")
        dprint(f"  [디버그] 콜 레코드 키: {list(call_records[0].keys())}")
        rows = _build_rows_from_grouped(call_records, put_records)
        if rows:
            return pd.DataFrame(rows)
        dprint("  [디버그] Call/Put 구조에서 행을 못 만듦 → 대체 구조 시도.")

    if flat_best is None:
        dprint(f"  [디버그] JSON 응답 {len(captured)}개를 스캔했지만 옵션체인으로 보이는 데이터를 못 찾음.")
        return pd.DataFrame()

    score, url, path, records = flat_best
    dprint(f"  [디버그] JSON 후보 채택(단일 리스트): {url}  경로={path}  점수={score}  레코드수={len(records)}")
    dprint(f"  [디버그] 첫 레코드 키: {list(records[0].keys())}")
    rows = _build_rows_from_records(records)
    return pd.DataFrame(rows)


def parse_from_html_table(html: str) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        dprint("  [디버그] HTML에서 <table> 태그를 아예 찾지 못함 (JS 그리드로 렌더링된 페이지일 가능성 높음).")
        return pd.DataFrame()

    dprint(f"  [디버그] 페이지에서 표 {len(tables)}개 발견. 각 표의 shape: {[t.shape for t in tables]}")
    target = None
    for t in tables:
        cols = [str(c) for c in t.columns]
        if any(re.search(r"strike", c, re.I) for c in cols):
            target = t
            break
    if target is None:
        return pd.DataFrame()

    cols = [str(c) for c in target.columns]
    strike_idx = next(i for i, c in enumerate(cols) if re.search(r"strike", c, re.I))
    left = target.iloc[:, :strike_idx]
    strike_col = target.iloc[:, strike_idx]
    right = target.iloc[:, strike_idx + 1:]

    def find_col(block: pd.DataFrame, pattern: str):
        for c in block.columns:
            if re.search(pattern, str(c), re.I):
                return block[c]
        return None

    call_oi = find_col(left, r"open\s*int")
    call_iv = find_col(left, r"impl.*vol|\biv\b")
    put_oi = find_col(right, r"open\s*int")
    put_iv = find_col(right, r"impl.*vol|\biv\b")
    if call_oi is None or put_oi is None:
        return pd.DataFrame()

    def clean_num(s):
        return pd.to_numeric(s.astype(str).str.replace(",", "").str.replace("%", "").str.strip(), errors="coerce")

    rows = []
    strikes = clean_num(strike_col)
    call_oi_c, put_oi_c = clean_num(call_oi), clean_num(put_oi)
    call_iv_c = clean_num(call_iv) if call_iv is not None else None
    put_iv_c = clean_num(put_iv) if put_iv is not None else None
    for i in range(len(target)):
        k = strikes.iloc[i]
        if pd.isna(k):
            continue
        if not pd.isna(call_oi_c.iloc[i]):
            rows.append({"strike": k, "type": "call", "openInterest": call_oi_c.iloc[i],
                         "impliedVolatility": (call_iv_c.iloc[i] / 100.0) if call_iv_c is not None else None})
        if not pd.isna(put_oi_c.iloc[i]):
            rows.append({"strike": k, "type": "put", "openInterest": put_oi_c.iloc[i],
                         "impliedVolatility": (put_iv_c.iloc[i] / 100.0) if put_iv_c is not None else None})
    return pd.DataFrame(rows)


def _finalize_capture_df(df: pd.DataFrame, html: str, symbol: str, cfg: dict, api_debug_text: str) -> pd.DataFrame:
    """capture_one()(Playwright)과 capture_one_requests()(requests) 둘 다 옵션 행을
    확보한 뒤 이어서 할 일(HTML 표 폴백, spot/만기 추정, 디버그 저장, 메타 컬럼 부착)이
    완전히 같아서 공통 함수로 뺐다."""
    if df.empty:
        dprint("  [디버그] HTML <table> 방식으로 재시도.")
        df = parse_from_html_table(html)

    if df.empty:
        debug_path = f"barchart_debug_{symbol}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        api_debug_path = f"barchart_api_{symbol}.txt"
        with open(api_debug_path, "w", encoding="utf-8") as f:
            f.write(api_debug_text or "")
        print(f"  [경고] {symbol}: 옵션 데이터를 전혀 못 찾았습니다.")
        return df

    override = MANUAL_OVERRIDE.get(symbol, {})
    spot = override.get("spot") or guess_spot(html)
    expiration = override.get("expiration") or guess_expiration(html)
    print(f"  [결과] spot 추정값: {spot} | 만기 추정값: {expiration} | 옵션 {len(df)}행")
    if spot is None or expiration is None:
        print(f"  [주의] {symbol}: spot 또는 만기를 자동으로 못 찾았습니다. "
              f"MANUAL_OVERRIDE['{symbol}'] = {{'spot': ..., 'expiration': 'YYYY-MM-DD'}} 로 채운 뒤 다시 실행하세요.")

    n_total = len(df)
    n_iv = int(df["impliedVolatility"].notna().sum()) if "impliedVolatility" in df.columns else 0
    n_gamma = int(df["gamma_barchart"].notna().sum()) if "gamma_barchart" in df.columns else 0
    print(f"  [진단] IV 있는 행: {n_iv}/{n_total} | bcdb 자체 gamma 있는 행: {n_gamma}/{n_total}")

    df["symbol"] = symbol
    df["spot"] = spot
    df["expiration"] = expiration
    df["contract_multiplier"] = cfg["multiplier"]
    df = df.dropna(subset=["openInterest"])
    df = df[df["openInterest"] > 0]
    return df


def capture_one_requests(symbol: str, cfg: dict) -> pd.DataFrame:
    """capture_one()과 동일한 결과를 Playwright(=Chromium) 없이 requests만으로 얻는다.

    배경: Barchart 옵션 페이지의 csrf_token(<meta name="csrf-token">)과
    XSRF-TOKEN 쿠키는 페이지를 처음 GET할 때 서버가 이미 응답에 실어 보내는
    정적인 값이다. JS를 실행해서 만들어지는 값이 아니라서, 이 둘만 얻으면
    실제 옵션 데이터가 오는 quotes/get API를 브라우저 없이도 그대로 호출할 수
    있다 — 2026-08, 운영 서버(구형 Ubuntu, glibc가 낮아 Playwright의 Chromium이
    아예 못 뜨는 환경)에서 실제로 성공까지 확인됨. Chromium/glibc 문제를
    완전히 피할 수 있는 경로라 이제 이게 기본 경로다 (run_capture_sync 참고).
    """
    print(f"\n=== {symbol} 캡처 중 (requests, 브라우저 없음) ===")
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        r = s.get(cfg["url"], timeout=20)
        html = r.text
    except Exception as e:
        dprint(f"  [디버그] 페이지 GET 실패: {e}")
        return pd.DataFrame()

    ticker = extract_api_symbol_from_config(html)
    if not ticker:
        m = re.search(r'"bc_ticker"\s*:\s*"([^"]+)"', html)
        ticker = m.group(1) if m else None
    ticker = normalize_options_symbol(symbol, ticker)
    if ticker and "*" in ticker:
        # cfg["url"]에 NQ*0/ES*0 같은 "최근월물" 별칭을 쓰는데, 정상이면 여기서
        # 나오는 ticker는 그 시점의 실제 계약 심볼(예: MQ1U26)로 풀려있어야 한다.
        # "*"가 그대로 남아있다는 건 Barchart가 별칭을 서버사이드에서 못 풀었다는
        # 뜻이므로, 이 상태로 API를 불러봐야 실패할 게 뻔해 미리 크게 경고한다.
        print(f"  [경고] {symbol}: 심볼이 안 풀린 채로 옴({ticker!r}). "
              f"Barchart의 최근월물 별칭(*0) 처리 방식이 바뀐 것으로 보입니다 — "
              f"TARGETS의 url을 만기 코드가 직접 박힌 형태(예: NQU26/options/MQ1U26)로 "
              f"되돌려야 할 수 있습니다.")
    elif ticker:
        print(f"  [확인] {symbol}: 이번 캡처에 사용된 실제 계약 심볼 = {ticker}")
    m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', html)
    csrf_token = m.group(1) if m else None
    xsrf_cookie = None
    for name, value in s.cookies.items():
        if name.upper() == "XSRF-TOKEN":
            from urllib.parse import unquote
            xsrf_cookie = unquote(value)
            break

    dprint(f"  [디버그] 페이지에서 추출한 메타: ticker={ticker} "
          f"csrf_token={'있음' if csrf_token else '없음'} "
          f"xsrf_cookie={'있음' if xsrf_cookie else '없음'}")

    df = pd.DataFrame()
    if ticker and csrf_token and xsrf_cookie:
        dprint("  [디버그] quotes/get 엔드포인트 직접 호출 시도 (requests)...")
        headers = {
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": cfg["url"],
            "X-CSRF-TOKEN": csrf_token,
            "X-XSRF-TOKEN": xsrf_cookie,
        }
        params = {
            "symbol": ticker, "list": "futures.options", "fields": CAPTURE_API_FIELDS,
            "meta": "field.shortName,field.description,field.type",
            "groupBy": "optionType", "orderBy": "strike", "orderDir": "asc", "raw": "1",
        }
        try:
            r2 = s.get(CAPTURE_API_URL, params=params, headers=headers, timeout=20)
            api_debug_text = f"status={r2.status_code}\n\n{r2.text}"
            if r2.status_code == 200 and r2.text:
                dprint(f"  [디버그] 직접 호출 응답 status=200, 길이={len(r2.text)}자.")
                df = parse_from_json_candidates([(CAPTURE_API_URL, r2.text)])
            else:
                dprint(f"  [디버그] 직접 호출 실패: status={r2.status_code}, 미리보기: {r2.text[:300]!r}")
        except Exception as e:
            api_debug_text = f"(요청 실패: {e})"
            dprint(f"  [디버그] 직접 호출 예외: {e}")
    else:
        api_debug_text = "(csrf_token/xsrf_cookie/ticker 중 하나를 못 찾아 API 호출을 생략함)"
        dprint(f"  [디버그] {api_debug_text}")

    return _finalize_capture_df(df, html, symbol, cfg, api_debug_text)


async def capture_one(symbol: str, cfg: dict, async_playwright) -> pd.DataFrame:
    print(f"\n=== {symbol} 캡처 중 ===")
    df = pd.DataFrame()
    html = ""
    api_debug_text = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))
        captured_json = []

        async def on_response(response):
            try:
                ct = response.headers.get("content-type", "")
                if "json" not in ct.lower():
                    return
                body = await response.text()
                if len(body) > MAX_BODY_BYTES:
                    return
                if re.search(r"strike", body, re.I):
                    captured_json.append((response.url, body))
            except Exception:
                pass

        page.on("response", on_response)
        await page.goto(cfg["url"], wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(2000)
        html = await page.content()

        meta = await extract_page_meta(page, html, symbol)
        dprint(f"  [디버그] 페이지에서 추출한 메타: ticker={meta.get('ticker')} "
              f"(출처: {meta.get('ticker_source')}) "
              f"csrf_token={'있음' if meta.get('csrf_token') else '없음'} "
              f"xsrf_cookie={'있음' if meta.get('xsrf_cookie') else '없음'}")
        _ticker = meta.get("ticker")
        if _ticker and "*" in _ticker:
            # requests 경로(capture_one_requests)와 동일한 이유의 경고.
            # TARGETS에 NQ*0/ES*0 같은 별칭을 쓰는데 여기서 안 풀린 채로 왔다는 뜻.
            print(f"  [경고] {symbol}: 심볼이 안 풀린 채로 옴({_ticker!r}). "
                  f"Barchart의 최근월물 별칭(*0) 처리 방식이 바뀐 것으로 보입니다 — "
                  f"TARGETS의 url을 만기 코드가 직접 박힌 형태로 되돌려야 할 수 있습니다.")
        elif _ticker:
            print(f"  [확인] {symbol}: 이번 캡처에 사용된 실제 계약 심볼 = {_ticker}")

        dprint("  [디버그] 1단계: quotes/get 엔드포인트 직접 호출 시도...")
        status, body = await try_direct_api(page, cfg["url"], meta, symbol)
        api_debug_text = f"status={status}\n\n{body if body else ''}"
        if status == 200 and body:
            dprint(f"  [디버그] 직접 호출 응답 status=200, 길이={len(body)}자.")
            df = parse_from_json_candidates([(CAPTURE_API_URL, body)])
        else:
            dprint(f"  [디버그] 직접 호출 실패 또는 빈 응답: status={status}, 내용 미리보기: {str(body)[:300]!r}")

        if df.empty:
            dprint(f"  [디버그] 2단계: 페이지 로드 중 가로챈 JSON 응답 {len(captured_json)}개 스캔")
            df = parse_from_json_candidates(captured_json)

        await browser.close()

    return _finalize_capture_df(df, html, symbol, cfg, api_debug_text)


def write_or_merge_futures_csv(csv_path: str, new_frames_by_symbol: dict) -> pd.DataFrame | None:
    """새로 캡처한 심볼의 행만 갈아끼우고, CSV에 이미 있던 다른 심볼 행은 보존한다
    (예: NQ만 재캡처해도 기존 ES 행이 CSV에서 사라지지 않음)."""
    existing = None
    if os.path.exists(csv_path):
        try:
            existing = pd.read_csv(csv_path)
        except Exception as e:
            print(f"  [경고] 기존 CSV 읽기 실패, 새로 씀: {e}")

    frames = []
    captured_symbols = set(new_frames_by_symbol.keys())
    if existing is not None and not existing.empty and "symbol" in existing.columns:
        frames.append(existing[~existing["symbol"].isin(captured_symbols)])
    for df in new_frames_by_symbol.values():
        if df is not None and not df.empty:
            frames.append(df)

    if not frames or all(f.empty for f in frames):
        return None

    full = pd.concat(frames, ignore_index=True)
    for c in FUTURES_CSV_COLUMNS:
        if c not in full.columns:
            full[c] = None
    full = full[FUTURES_CSV_COLUMNS]
    full.to_csv(csv_path, index=False)
    return full


def _build_greeks_rows(records: list) -> list:
    """'Volatility & Greeks' 페이지(옵션 프라이스 페이지와 다른 뷰) 전용 파서.
    이 페이지 응답에는 openInterest 자체가 없는 게 정상이라(그릭스만 보여주는
    화면이라서), 그걸 필수 조건으로 걸지 않는다 — 그 점만 빼면
    _build_rows_from_records의 "prefix 없는" 분기와 로직이 같다."""
    rows = []
    for r in records:
        strike = _to_float(_get_field(r, r"strike"))
        if strike is None:
            continue
        side_raw = _get_field(r, r"^(type|side|put ?call|option ?type)$")
        side = str(side_raw).lower() if side_raw is not None else ""
        opt_type = "call" if side[:1] == "c" else ("put" if side[:1] == "p" else None)
        if opt_type is None:
            continue
        iv = _normalize_iv(_to_float(_get_field(r, r"impl.*vol|\biv\b")))
        delta = _to_float(_get_field(r, r"^delta$"))
        gamma = _to_float(_get_field(r, r"^gamma$"))
        theta = _to_float(_get_field(r, r"^theta$"))
        vega = _to_float(_get_field(r, r"^vega$"))
        if iv is None and delta is None and gamma is None:
            continue  # 아무 그릭스도 못 찾았으면 병합할 가치가 없으니 버림
        rows.append({
            "strike": strike, "type": opt_type, "impliedVolatility": iv,
            "delta_barchart": delta, "gamma_barchart": gamma,
            "theta_barchart": theta, "vega_barchart": vega,
        })
    return rows


def parse_greeks_from_json_candidates(captured: list) -> pd.DataFrame:
    """parse_from_json_candidates와 후보 탐색 로직은 완전히 같다(재사용) —
    마지막에 행을 만드는 단계만 OI를 요구하지 않는 _build_greeks_rows를 쓴다."""
    grouped_best = None
    flat_best = None
    for url, body in captured:
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            continue
        for path, call_records, put_records in _find_call_put_groups(data):
            score = _score_candidate(call_records) + _score_candidate(put_records)
            if grouped_best is None or score > grouped_best[0]:
                grouped_best = (score, url, path, call_records, put_records)
        for path, records in _find_candidate_lists(data):
            score = _score_candidate(records)
            if score >= 5 and (flat_best is None or score > flat_best[0]):
                flat_best = (score, url, path, records)

    if grouped_best is not None:
        score, url, path, call_records, put_records = grouped_best
        dprint(f"  [디버그-그릭스] Call/Put 분리 구조 채택: {url}  경로={path}  점수={score}")
        rows = _build_rows_from_grouped(call_records, put_records)  # 이미 그릭스 포함해서 만듦
        if rows:
            return pd.DataFrame(rows)
        dprint("  [디버그-그릭스] Call/Put 구조에서 행을 못 만듦 → 대체 구조 시도.")

    if flat_best is None:
        dprint(f"  [디버그-그릭스] JSON 응답 {len(captured)}개를 스캔했지만 그릭스 데이터를 못 찾음.")
        return pd.DataFrame()

    score, url, path, records = flat_best
    dprint(f"  [디버그-그릭스] JSON 후보 채택(단일 리스트): {url}  경로={path}  점수={score}  레코드수={len(records)}")
    dprint(f"  [디버그-그릭스] 첫 레코드 키: {list(records[0].keys())}")
    rows = _build_greeks_rows(records)
    return pd.DataFrame(rows)


async def capture_greeks_one(symbol: str, cfg: dict, async_playwright) -> pd.DataFrame:
    """'Volatility & Greeks' 페이지를 캡처해서 (strike, type, impliedVolatility,
    delta_barchart, gamma_barchart, theta_barchart, vega_barchart)만 돌려준다.
    capture_one()과 페이지 로드/네트워크 가로채기 방식은 거의 동일하지만,
    _finalize_capture_df()를 거치지 않는다 — 그 함수는 openInterest 기준으로
    필터링하는데 이 페이지엔 OI가 아예 없어서 전부 걸러져 버리기 때문이다.
    반환된 결과는 run_capture_sync()에서 옵션 프라이스 페이지 결과와
    (strike, type) 기준으로 병합해서 쓴다."""
    print(f"\n=== {symbol} Volatility & Greeks 캡처 중 ===")
    captured_json = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ))

        async def on_response(response):
            try:
                ct = response.headers.get("content-type", "")
                if "json" not in ct.lower():
                    return
                body = await response.text()
                if len(body) > MAX_BODY_BYTES:
                    return
                if re.search(r"strike", body, re.I):
                    captured_json.append((response.url, body))
            except Exception:
                pass

        page.on("response", on_response)
        try:
            await page.goto(cfg["url"], wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"  [오류] {symbol} Greeks 페이지 로드 실패: {e}")
            await browser.close()
            return pd.DataFrame()
        await browser.close()

    df = parse_greeks_from_json_candidates(captured_json)
    n_iv = int(df["impliedVolatility"].notna().sum()) if not df.empty and "impliedVolatility" in df.columns else 0
    print(f"  [결과] Greeks {len(df)}행 확보 (IV 있는 행 {n_iv}개)")
    return df


def _merge_greeks(df_main: pd.DataFrame, df_greeks: pd.DataFrame) -> pd.DataFrame:
    """옵션 프라이스 페이지 결과(df_main: strike/type/openInterest/가격 등)에
    Greeks 페이지 결과(df_greeks: strike/type/IV/그릭스)를 (strike, type) 기준으로
    왼쪽 조인한다. df_greeks가 비어있으면(캡처 실패 등) df_main을 그대로 돌려준다
    (그릭스 없이도 콜월/풋월 등 OI 기반 분석은 계속 가능하게)."""
    if df_greeks is None or df_greeks.empty:
        return df_main
    greek_cols = ["strike", "type", "impliedVolatility", "delta_barchart",
                  "gamma_barchart", "theta_barchart", "vega_barchart"]
    df_greeks = df_greeks[[c for c in greek_cols if c in df_greeks.columns]]
    merged = df_main.drop(
        columns=[c for c in greek_cols if c != "strike" and c != "type" and c in df_main.columns]
    ).merge(df_greeks, on=["strike", "type"], how="left")
    return merged


def run_capture_sync(symbols: list, csv_path: str):
    """symbols(예: ["NQ"] 또는 ["NQ","ES"])를 Barchart에서 캡처해 csv_path에 저장/병합.

    2026-08부터: 먼저 requests만으로(capture_one_requests, 브라우저 불필요) 캡처를
    시도한다. Chromium/glibc 문제를 겪는 구형 서버에서도 이 경로로 캡처가 되는 게
    실서버에서 확인됐다. 이 방식으로 못 얻은 심볼만, playwright가 설치돼 있으면
    Playwright(capture_one)로 재시도한다 — playwright가 아예 없어도 requests 경로가
    성공하면 전혀 문제없다."""
    results = {}
    need_playwright_retry = []
    for sym in symbols:
        cfg = TARGETS[sym]
        try:
            df = capture_one_requests(sym, cfg)
        except Exception as e:
            print(f"  [오류] {sym} requests 캡처 실패: {e}")
            df = pd.DataFrame()
        if df.empty:
            need_playwright_retry.append(sym)
        else:
            results[sym] = df

    if need_playwright_retry:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print(f"  [경고] requests 방식으로 못 받은 심볼: {need_playwright_retry}. "
                  f"playwright가 설치돼 있지 않아 재시도를 건너뜁니다 "
                  f"(설치: pip install playwright && playwright install --with-deps chromium).")
        else:
            print(f"  [정보] requests 방식으로 못 받은 심볼 {need_playwright_retry}을 "
                  f"Playwright로 재시도합니다...")

            async def _run():
                out = {}
                for sym in need_playwright_retry:
                    cfg = TARGETS[sym]
                    try:
                        out[sym] = await capture_one(sym, cfg, async_playwright)
                    except Exception as e:
                        print(f"  [오류] {sym} Playwright 캡처 실패: {e}")
                        out[sym] = pd.DataFrame()
                return out

            try:
                pw_results = asyncio.run(_run())
            except RuntimeError:
                import nest_asyncio
                nest_asyncio.apply()
                pw_results = asyncio.get_event_loop().run_until_complete(_run())
            results.update(pw_results)

    # --- Greeks 병합 (2026-08 말 이후: 옵션 프라이스 페이지는 IV/그릭스를 안 줘서
    # 별도 "Volatility & Greeks" 페이지에서 따로 받아와 strike+type 기준으로 합친다).
    # 이 단계는 항상 Playwright가 필요하다(그릭스 페이지도 requests로는 403 확인됨).
    # 실패해도 기존 OI 기반 데이터는 그대로 살아있으니 조용히 넘어간다.
    symbols_with_data = [s for s in symbols if s in results and not results[s].empty]
    if symbols_with_data:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("  [정보] playwright가 없어 Greeks(IV/델타/감마) 병합은 건너뜁니다 "
                  "(OI 기반 콜월/풋월 분석은 계속 가능).")
        else:
            async def _run_greeks():
                out = {}
                for sym in symbols_with_data:
                    gcfg = TARGETS_GREEKS.get(sym)
                    if not gcfg:
                        continue
                    try:
                        out[sym] = await capture_greeks_one(sym, gcfg, async_playwright)
                    except Exception as e:
                        print(f"  [오류] {sym} Greeks 캡처 실패: {e}")
                        out[sym] = pd.DataFrame()
                return out

            try:
                greeks_results = asyncio.run(_run_greeks())
            except RuntimeError:
                import nest_asyncio
                nest_asyncio.apply()
                greeks_results = asyncio.get_event_loop().run_until_complete(_run_greeks())

            for sym, df_greeks in greeks_results.items():
                results[sym] = _merge_greeks(results[sym], df_greeks)
                n_iv = int(results[sym]["impliedVolatility"].notna().sum())
                print(f"  [병합 완료] {sym}: IV 있는 행 {n_iv}/{len(results[sym])}")

    full = write_or_merge_futures_csv(csv_path, results)
    if full is None:
        sys.exit("캡처된 데이터가 없습니다. 위 [디버그]/[경고] 로그를 확인해주세요.")
    print(f"\n[캡처 완료] CSV 저장/갱신됨 (전체 {len(full)}행)")
    print(full.groupby("symbol").size())


def run_futures_mode(args):
    """--ticker가 NQ/NQ=F/ES/ES=F일 때의 전체 흐름 (gamma_flip_from_csv.py와 동일 분석 로직 +
    필요시 Barchart 캡처를 이 안에서 직접 수행)."""
    symbol = FUTURES_TICKER_ALIASES[args.ticker.strip().upper()]

    # 파일이 있어도 "그 안에 지금 요청한 심볼이 있는지"까지 확인해야 한다.
    # (버그였던 부분: 파일 존재 여부만 보면 NQ만 캡처된 CSV로 ES=F를 돌릴 때
    # 캡처를 건너뛰고 바로 "ES 없음" 에러가 났음.)
    csv_has_symbol = False
    if os.path.exists(args.futures_csv):
        try:
            existing_symbols = set(pd.read_csv(args.futures_csv, usecols=["symbol"])["symbol"].unique())
            csv_has_symbol = symbol in existing_symbols
        except Exception as e:
            print(f"  [경고] 기존 CSV 확인 실패, 새로 캡처합니다: {e}")

    need_capture = args.recapture or not csv_has_symbol
    if need_capture:
        if args.no_capture:
            sys.exit(f"{symbol} 데이터가 없습니다. --no-capture가 설정돼 있어 "
                      f"자동 캡처를 건너뜁니다 — CSV 캡처 코드를 먼저 돌리거나 --no-capture를 빼세요.")
        symbols_to_capture = list(TARGETS.keys()) if args.capture_both else [symbol]
        if args.recapture:
            reason = "재캡처 요청됨(--recapture)"
        elif not os.path.exists(args.futures_csv):
            reason = "CSV 없음"
        else:
            reason = f"CSV에 {symbol} 데이터가 아직 없음"
        print(f"[0/3] 자동 캡처 시작 ({reason}): {symbols_to_capture} "
              f"— 시간이 좀 걸릴 수 있습니다...")
        run_capture_sync(symbols_to_capture, args.futures_csv)
        print()

    print(f"[1/3] CSV에서 {symbol} 로딩 중... "
          f"(yfdb는 CME 선물옵션을 지원하지 않아 사전 캡처된 CSV를 씁니다)")
    chain, spot, multiplier = load_futures_symbol(args.futures_csv, symbol)
    print(f"      spot: {spot:.2f} | 계약승수: {multiplier} | 옵션 {len(chain)}행 | "
          f"만기: {sorted(chain['expiration'].unique())}")

    n_iv_calls = int(((chain["type"] == "call") & chain["impliedVolatility"].notna() & (chain["impliedVolatility"] > 0)).sum())
    n_iv_puts = int(((chain["type"] == "put") & chain["impliedVolatility"].notna() & (chain["impliedVolatility"] > 0)).sum())
    n_gamma = int(chain["gamma_barchart"].notna().sum())
    print(f"      실제 IV 있는 행: 콜 {n_iv_calls} / 풋 {n_iv_puts}  |  bcdb gamma 있는 행: {n_gamma}행")

    # bcdb가 IV를 거의 안 주므로(대부분 N/A), delta_bcdb로부터 Black-76 역산을 시도해
    # "유효 IV" 커버리지를 넓힌다 (iv_effective 컬럼: 실제 IV 우선, 없으면 delta 역산).
    chain = derive_effective_iv_futures(chain, spot, r=0.04)
    n_eff_calls = int(((chain["type"] == "call") & chain["iv_effective"].notna()).sum())
    n_eff_puts = int(((chain["type"] == "put") & chain["iv_effective"].notna()).sum())
    n_uniq_root = int((chain["iv_source"] == "delta_unique").sum())
    n_smile = int((chain["iv_source"] == "delta_smile").sum())
    n_from_delta = n_uniq_root + n_smile
    print(f"      delta 역산으로 IV 추가 확보: {n_from_delta}행 "
          f"(유일근 {n_uniq_root} / 근 2개라 스마일로 선택 {n_smile})  ->  "
          f"유효 IV(실제+역산): 콜 {n_eff_calls} / 풋 {n_eff_puts}")
    use_bs_mode = n_eff_calls >= args.futures_min_iv_rows and n_eff_puts >= args.futures_min_iv_rows

    print("\n===== 결과 =====")
    print(f"티커: {args.ticker} (내부 심볼: {symbol})")
    print(f"현재가: {spot:.2f}")

    if use_bs_mode:
        print("[2/3] 모드 A (Black-76 스캔): 가상 spot 가격대별 GEX 계산 중...")
        if n_from_delta > 0:
            print(f"      (참고: {n_from_delta}행은 bcdb의 실제 IV가 아니라 delta_bcdb를 "
                  f"Black-76으로 역산한 근사 IV를 사용합니다)")
        price_grid, gex_values = compute_gex_curve_futures_bs(chain, spot, multiplier, 0.04, args.range_pct)
        crossings = find_flip_point(price_grid, gex_values)
        current_gex = np.interp(spot, price_grid, gex_values)
        regime = "포지티브 감마" if current_gex > 0 else "네거티브 감마"
        print(f"현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치)")
        print(f"현재 레짐 추정: {regime}")
        if crossings:
            nearest = min(crossings, key=lambda x: abs(x - spot))
            print(f"감마 플립 레벨: {nearest:.2f}  (교차점 {len(crossings)}개, spot={spot:.2f} 대비 "
                  f"{(nearest - spot):+.1f}pt / {(nearest - spot) / spot * 100:+.2f}%)")
        else:
            print("스캔 범위 내 교차점 없음 — --range-pct를 늘려보세요.")
    elif n_gamma > 0:
        print("[2/3] 모드 B (bcdb 자체 gamma 사용): IV가 부족해 BS 스캔은 생략하고, "
              "bcdb가 계산해 내려준 gamma로 현재 시점 GEX만 계산합니다.")
        current_gex, n_c, n_p = compute_current_gex_from_barchart_gamma(chain, spot, multiplier)
        regime = "포지티브 감마" if current_gex > 0 else "네거티브 감마"
        print(f"현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치, 콜 {n_c}행/풋 {n_p}행 사용)")
        print(f"현재 레짐 추정: {regime}")
        print("감마 플립 '가격 레벨'은 계산 불가 — IV도 delta 역산도 실패해서 가상 spot으로 "
              "재계산할 수 없습니다. 현재 spot이 어느 쪽에 있는지(레짐)만 참고하세요.")
        # Barchart gamma는 소수 4자리로 반올림돼 내려온다. NQ처럼 gamma가 1e-4 수준인
        # 종목은 값이 사실상 0/0.0001/0.0002 몇 단계로만 양자화돼서 오차가 매우 크다.
        gvals = chain["gamma_barchart"].dropna()
        n_zero = int((gvals == 0).sum())
        n_uniq = gvals.nunique()
        if n_uniq <= 5 or n_zero > 0:
            zero_oi = float(chain.loc[chain["gamma_barchart"] == 0, "openInterest"].sum())
            total_oi = float(chain["openInterest"].sum())
            print(f"  [경고] bcdb gamma는 소수 4자리 반올림 값이라 고유값이 {n_uniq}종류뿐이고, "
                  f"{n_zero}행은 gamma=0으로 내려와 GEX 기여가 통째로 누락됩니다 "
                  f"(누락 OI {zero_oi:,.0f} / 전체 {total_oi:,.0f} = {zero_oi/max(total_oi,1):.0%}). "
                  f"이 모드의 GEX 절대값은 오차가 크니 레짐 방향 정도로만 보세요.")
    else:
        print("[2/3] IV도, bcdb gamma도 둘 다 없어 GEX/레짐/플립 계산이 불가능합니다. "
              "CSV 캡처 코드를 다시 실행해서 CSV를 새로 받아보세요.")

    print("\n[3/3] 콜월/풋월 탐색 중 (단일 최댓값 방식 + 스무딩 방식 둘 다 계산)...")
    walls = find_walls_futures_raw(chain)
    walls_sm = find_walls_futures_smoothed(chain, spot, args.futures_wall_bandwidth_pct)

    print("[단일 최댓값 방식]")
    if "call_wall_strike" in walls:
        d = walls["call_wall_strike"] - spot
        print(f"  콜월: {walls['call_wall_strike']:.2f}  (콜 OI {walls['call_wall_oi']:,}, spot 대비 {d:+.0f}pt / {d/spot*100:+.2f}%)")
    if "put_wall_strike" in walls:
        d = walls["put_wall_strike"] - spot
        print(f"  풋월: {walls['put_wall_strike']:.2f}  (풋 OI {walls['put_wall_oi']:,}, spot 대비 {d:+.0f}pt / {d/spot*100:+.2f}%)")

    print(f"[스무딩 방식] (커널 폭={args.futures_wall_bandwidth_pct*100:.1f}% of spot)")
    if "call_wall_strike" in walls_sm:
        d = walls_sm["call_wall_strike"] - spot
        print(f"  콜월: {walls_sm['call_wall_strike']:.2f}  (근방 OI 합 {walls_sm['call_wall_region_oi']:,.0f}, spot 대비 {d:+.0f}pt / {d/spot*100:+.2f}%)")
    if "put_wall_strike" in walls_sm:
        d = walls_sm["put_wall_strike"] - spot
        print(f"  풋월: {walls_sm['put_wall_strike']:.2f}  (근방 OI 합 {walls_sm['put_wall_region_oi']:,.0f}, spot 대비 {d:+.0f}pt / {d/spot*100:+.2f}%)")

    print("\n주의: 표준 근사 가정(딜러 콜숏/풋롱) 기반이며, spot/만기는 캡처 시점 값입니다.")
    print("실시간이 아니라 스냅샷이므로, 최신 값이 필요하면 CSV 캡처 코드를 다시 돌려 CSV를 갱신하세요.")


def main():
    parser = argparse.ArgumentParser(description="감마 플립(Zero Gamma) 레벨 계산기")
    parser.add_argument("--ticker", default="SPY",
                         help="옵션 유동성이 있는 티커 (기본: SPY). NQ/NQ=F/ES/ES=F를 주면 "
                              "bcdb CSV 기반 선물옵션 경로로 자동 전환됩니다.")
    parser.add_argument("--max-days", type=int, default=45, help="포함할 최대 만기일수 (기본: 45일, ETF 경로에서만 사용)")
    parser.add_argument("--range-pct", type=float, default=0.15, help="현재가 대비 스캔 범위 (기본: ±15%%)")
    # NQ=F / ES=F 경로 전용 옵션
    parser.add_argument("--futures-csv", default=FUTURES_CSV_DEFAULT,
                         help="CSV 캡처 코드 결과 CSV 경로 (NQ=F/ES=F 전용, 기본: barchart_options_capture.csv)")
    parser.add_argument("--futures-min-iv-rows", type=int, default=FUTURES_MIN_IV_ROWS_DEFAULT,
                         help="콜/풋 각각 이 개수 이상 유효 IV가 있어야 BS 스캔 모드 사용 (NQ=F/ES=F 전용, 기본 5)")
    parser.add_argument("--futures-wall-bandwidth-pct", type=float, default=FUTURES_WALL_BANDWIDTH_PCT_DEFAULT,
                         help="스무딩 콜월/풋월용 가우시안 커널 폭, spot 대비 비율 (NQ=F/ES=F 전용, 기본 0.01)")
    parser.add_argument("--recapture", action="store_true",
                         help="CSV가 이미 있어도 bcdb에서 강제로 새로 캡처 (NQ=F/ES=F 전용)")
    parser.add_argument("--capture-both", action="store_true",
                         help="캡처가 필요할 때 요청한 심볼만이 아니라 NQ/ES 둘 다 한 번에 캡처 (NQ=F/ES=F 전용)")
    parser.add_argument("--no-capture", action="store_true",
                         help="CSV가 없어도 자동 캡처를 시도하지 않고 바로 에러 (NQ=F/ES=F 전용)")
    parser.add_argument("--debug", action="store_true",
                         help="[디버그] 태그 붙은 상세 캡처/파싱 로그를 출력 (기본은 꺼짐)")
    # 외부 실행 환경이 자체적으로 추가하는 인자를 무시 (다른 스크립트들과 동일 이유)
    args, _unknown = parser.parse_known_args()

    if args.debug:
        global DEBUG_VERBOSE
        DEBUG_VERBOSE = True

    if args.ticker.strip().upper() in FUTURES_TICKER_ALIASES:
        run_futures_mode(args)
        return

    print(f"[1/4] {args.ticker} 옵션체인 로딩 중 (만기 {args.max_days}일 이내)...")
    chain, spot = fetch_chain(args.ticker, args.max_days)
    n_exp = chain["expiration"].nunique()
    print(f"      현재가: {spot:.2f} | 만기 {n_exp}개 | 옵션 {len(chain)}건 로드 완료")

    print("[2/4] 가상 spot 가격대별 넷 감마 익스포저(GEX) 계산 중...")
    price_grid, gex_values = compute_gex_curve(chain, spot, price_range_pct=args.range_pct)

    print("[3/4] 감마 플립 지점 탐색 중...")
    crossings = find_flip_point(price_grid, gex_values)

    print("[4/4] 콜월 / 풋월(OI 최댓값 행사가) 탐색 중...")
    walls_by_exp = find_walls(chain)
    walls_agg = find_walls_aggregate(chain)

    current_gex = np.interp(spot, price_grid, gex_values)
    regime = "포지티브 감마" if current_gex > 0 else "네거티브 감마"

    print("\n===== 결과 =====")
    print(f"티커: {args.ticker}")
    print(f"현재가: {spot:.2f}")
    print(f"현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치)")
    print(f"현재 레짐 추정: {regime}")

    if crossings:
        nearest = min(crossings, key=lambda x: abs(x - spot))
        print(f"감마 플립(Zero Gamma) 레벨: {nearest:.2f}  (스캔 범위 내 교차점 {len(crossings)}개: {[round(c,2) for c in crossings]})")
        if spot > nearest:
            print(f"-> 현재가({spot:.2f})가 플립 레벨({nearest:.2f}) 위에 있음: 포지티브 감마 구간")
        else:
            print(f"-> 현재가({spot:.2f})가 플립 레벨({nearest:.2f}) 아래에 있음: 네거티브 감마 구간")
    else:
        print(f"스캔 범위(±{args.range_pct*100:.0f}%) 내에서 부호 교차가 없습니다. --range-pct 값을 늘려보세요.")

    print("\n===== 콜월 / 풋월 =====")
    if walls_agg:
        cw = walls_agg.get("call_wall_strike")
        cw_oi = walls_agg.get("call_wall_oi")
        pw = walls_agg.get("put_wall_strike")
        pw_oi = walls_agg.get("put_wall_oi")
        print(f"[{args.ticker}, 만기 {args.max_days}일 이내 전체 합산 기준]")
        if cw is not None:
            print(f"  콜월: {cw:.2f}  (콜 OI {cw_oi:,})")
        if pw is not None:
            print(f"  풋월: {pw:.2f}  (풋 OI {pw_oi:,})")

    print(f"\n[만기별 상세 — 상위 {min(5, len(walls_by_exp))}개 만기]")
    print(walls_by_exp.head(5).to_string(index=False))

    print("\n주의: 이 계산은 '딜러가 콜은 숏, 풋은 롱'이라는 표준 근사 가정을 사용합니다.")
    print("실제 딜러 포지셔닝과는 차이가 있을 수 있으며, 참고용 추정치입니다.")
    print("콜월/풋월은 순수 오픈인터레스트 기준입니다 — 달러 감마 가중 방식과는 다른 행사가가 나올 수 있습니다.")


if __name__ == "__main__":
    main()
