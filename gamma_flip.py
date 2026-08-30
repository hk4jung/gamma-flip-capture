import base64 as _b64
_κ = 39460
def _ρ(s):
    return _b64.b64decode(s.encode('ascii')).decode('utf-8')

import argparse
import asyncio
import html as html_module
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
    sys.exit(_ρ('eWZkYuqwgCDtlYTsmpTtlanri4jri6Q6IHBpcCBpbnN0YWxsIHlmaW5hbmNl'))
try:
    import requests
except ImportError:
    sys.exit(_ρ('cmVxdWVzdHPqsIAg7ZWE7JqU7ZWp64uI64ukOiBwaXAgaW5zdGFsbCByZXF1ZXN0cw=='))
DEBUG_VERBOSE = os.environ.get(_ρ('R0FNTUFfRkxJUF9ERUJVRw=='), _ρ('MA==')) == _ρ('MQ==')

def dprint(*args, **kwargs):
    if DEBUG_VERBOSE:
        print(*args, **kwargs)
FUTURES_TICKER_ALIASES = {_ρ('TlE='): _ρ('TlE='), _ρ('TlE9Rg=='): _ρ('TlE='), _ρ('RVM='): _ρ('RVM='), _ρ('RVM9Rg=='): _ρ('RVM=')}
FUTURES_CSV_DEFAULT = _ρ('YmFyY2hhcnRfb3B0aW9uc19jYXB0dXJlLmNzdg==')
FUTURES_MIN_IV_ROWS_DEFAULT = 39457 ^ _κ
FUTURES_WALL_BANDWIDTH_PCT_DEFAULT = 0.01
TARGETS = {_ρ('TlE='): {_ρ('dXJs'): _ρ('aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2Z1dHVyZXMvcXVvdGVzL05RKjAvb3B0aW9ucz9tb25leW5lc3M9YWxsUm93cyZmdXR1cmVzT3B0aW9uc1ZpZXc9bWVyZ2Vk'), _ρ('bXVsdGlwbGllcg=='): 20.0}, _ρ('RVM='): {_ρ('dXJs'): _ρ('aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2Z1dHVyZXMvcXVvdGVzL0VTKjAvb3B0aW9ucz9tb25leW5lc3M9YWxsUm93cyZmdXR1cmVzT3B0aW9uc1ZpZXc9bWVyZ2Vk'), _ρ('bXVsdGlwbGllcg=='): 50.0}}
TARGETS_GREEKS = {_ρ('TlE='): {_ρ('dXJs'): _ρ('aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2Z1dHVyZXMvcXVvdGVzL05RKjAvdm9sYXRpbGl0eS1ncmVla3M/bW9uZXluZXNzPWFsbFJvd3MmZnV0dXJlc09wdGlvbnNWaWV3PW1lcmdlZA==')}, _ρ('RVM='): {_ρ('dXJs'): _ρ('aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL2Z1dHVyZXMvcXVvdGVzL0VTKjAvdm9sYXRpbGl0eS1ncmVla3M/bW9uZXluZXNzPWFsbFJvd3MmZnV0dXJlc09wdGlvbnNWaWV3PW1lcmdlZA==')}}
MANUAL_OVERRIDE = {}
MAX_BODY_BYTES = 5034340 ^ _κ
CAPTURE_API_URL = _ρ('aHR0cHM6Ly93d3cuYmFyY2hhcnQuY29tL3Byb3hpZXMvY29yZS1hcGkvdjEvcXVvdGVzL2dldA==')
CAPTURE_API_FIELDS = _ρ('c3RyaWtlLG9wZW5QcmljZSxoaWdoUHJpY2UsbG93UHJpY2UsbGFzdFByaWNlLHByaWNlQ2hhbmdlLGJpZFByaWNlLGFza1ByaWNlLHZvbHVtZSxvcGVuSW50ZXJlc3QscHJlbWl1bSx0cmFkZVRpbWUsbG9uZ1N5bWJvbCxvcHRpb25UeXBlLHN5bWJvbCxpbXBsaWVkVm9sYXRpbGl0eSxkZWx0YSxnYW1tYSx0aGV0YSx2ZWdhLHJobyxleHBpcmF0aW9uRGF0ZSxkYXlzVG9FeHBpcmF0aW9u')
FUTURES_CSV_COLUMNS = [_ρ('c3ltYm9s'), _ρ('c3RyaWtl'), _ρ('dHlwZQ=='), _ρ('b3BlbkludGVyZXN0'), _ρ('aW1wbGllZFZvbGF0aWxpdHk='), _ρ('ZGVsdGFfYmFyY2hhcnQ='), _ρ('Z2FtbWFfYmFyY2hhcnQ='), _ρ('dGhldGFfYmFyY2hhcnQ='), _ρ('dmVnYV9iYXJjaGFydA=='), _ρ('ZXhwaXJhdGlvbg=='), _ρ('c3BvdA=='), _ρ('Y29udHJhY3RfbXVsdGlwbGllcg==')]

def bs_gamma(S, K, T, sigma, r=0.05):
    S = np.asarray(S, dtype=float)
    T = np.maximum(np.asarray(T, dtype=float), 1e-06)
    sigma = np.maximum(np.asarray(sigma, dtype=float), 0.0001)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    return gamma

def b76_delta(F, K, T, sigma, r, opt_type: str):
    F = np.asarray(F, dtype=float)
    T = max(float(T), 1e-06)
    sigma = max(float(sigma), 1e-06)
    d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / (sigma * np.sqrt(T))
    disc = np.exp(-r * T)
    return disc * norm.cdf(d1) if opt_type == _ρ('Y2FsbA==') else -disc * norm.cdf(-d1)

def b76_gamma(F, K, T, sigma, r=0.04):
    F = np.asarray(F, dtype=float)
    T = np.maximum(np.asarray(T, dtype=float), 1e-06)
    sigma = np.maximum(np.asarray(sigma, dtype=float), 0.0001)
    d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / (sigma * np.sqrt(T))
    disc = np.exp(-r * T)
    return disc * norm.pdf(d1) / (F * sigma * np.sqrt(T))

def solve_iv_roots_from_delta_b76(delta, F, K, T, r, opt_type: str, sigma_grid=None):
    if sigma_grid is None:
        sigma_grid = np.linspace(0.005, 3.0, 40596 ^ _κ)
    T_ = max(float(T), 1e-06)
    d1_grid = (np.log(F / K) + 0.5 * sigma_grid ** 2 * T_) / (sigma_grid * np.sqrt(T_))
    disc = np.exp(-r * T_)
    delta_grid = disc * norm.cdf(d1_grid) if opt_type == _ρ('Y2FsbA==') else -disc * norm.cdf(-d1_grid)
    resid = delta_grid - delta
    absresid = np.abs(resid)
    roots = []
    for i in range(1, len(sigma_grid) - 1):
        if absresid[i] < absresid[i - 1] and absresid[i] <= absresid[i + 1] and (absresid[i] < 0.001):
            lo, hi = (sigma_grid[i - 1], sigma_grid[i + 1])
            try:
                if resid[i - 1] * resid[i + 1] < 0:
                    root = brentq(lambda s: b76_delta(F, K, T, s, r, opt_type) - delta, lo, hi, xtol=1e-10)
                else:
                    root = sigma_grid[i]
            except Exception:
                root = sigma_grid[i]
            if abs(b76_delta(F, K, T, root, r, opt_type) - delta) <= 0.001 and 0.02 <= root <= 2.0:
                roots.append(root)
    roots = sorted(roots)
    deduped = []
    for x in roots:
        if not deduped or abs(x - deduped[-1]) > 0.0001:
            deduped.append(x)
    return deduped

def implied_vol_from_delta_b76(delta, F, K, T, r, opt_type: str, reference_iv=None, sigma_grid=None):
    roots = solve_iv_roots_from_delta_b76(delta, F, K, T, r, opt_type, sigma_grid)
    if not roots:
        return (None, None)
    if reference_iv is not None and np.isfinite(reference_iv):
        best = min(roots, key=lambda s: abs(s - reference_iv))
    else:
        best = roots[0]
    return (best, abs(b76_delta(F, K, T, best, r, opt_type) - delta))

def _fit_reference_smile(anchors):
    if len(anchors) >= 39463 ^ _κ:
        xs = np.array([a[0] for a in anchors])
        ys = np.array([a[1] for a in anchors])
        b, a = np.polyfit(xs, ys, 1)
        return lambda lm: float(np.clip(a + b * lm, 0.02, 2.0))
    if anchors:
        med = float(np.median([a[1] for a in anchors]))
        return lambda lm: med
    return None

def derive_effective_iv_futures(chain: pd.DataFrame, spot: float, r: float=0.04) -> pd.DataFrame:
    chain = chain.copy()
    n = len(chain)
    iv_eff = [np.nan] * n
    iv_src = [_ρ('bm9uZQ==')] * n
    roots_cache = {}
    anchors = []
    for pos in range(n):
        row = chain.iloc[pos]
        real_iv = row.get(_ρ('aW1wbGllZFZvbGF0aWxpdHk='))
        if pd.notna(real_iv) and real_iv > 0:
            iv_eff[pos] = float(real_iv)
            iv_src[pos] = _ρ('cmVhbA==')
            anchors.append((np.log(float(row[_ρ('c3RyaWtl')]) / spot), float(real_iv)))
            continue
        delta = row.get(_ρ('ZGVsdGFfYmFyY2hhcnQ='))
        if pd.isna(delta) or pd.isna(row.get(_ρ('VA=='))):
            continue
        roots = solve_iv_roots_from_delta_b76(float(delta), spot, float(row[_ρ('c3RyaWtl')]), float(row[_ρ('VA==')]), r, row[_ρ('dHlwZQ==')])
        roots_cache[pos] = roots
        if len(roots) == 1:
            iv_eff[pos] = roots[0]
            iv_src[pos] = _ρ('ZGVsdGFfdW5pcXVl')
            anchors.append((np.log(float(row[_ρ('c3RyaWtl')]) / spot), roots[0]))
    ref_fn = _fit_reference_smile(anchors)
    for pos, roots in roots_cache.items():
        if iv_src[pos] != _ρ('bm9uZQ==') or not roots:
            continue
        lm = np.log(float(chain.iloc[pos][_ρ('c3RyaWtl')]) / spot)
        iv_eff[pos] = roots[0] if ref_fn is None else min(roots, key=lambda s: abs(s - ref_fn(lm)))
        iv_src[pos] = _ρ('ZGVsdGFfc21pbGU=')
    chain[_ρ('aXZfZWZmZWN0aXZl')] = iv_eff
    chain[_ρ('aXZfc291cmNl')] = iv_src
    return chain

def fetch_chain(ticker: str, max_days: int) -> pd.DataFrame:
    tk = yf.Ticker(ticker)
    spot = tk.history(period=_ρ('MWQ='))[_ρ('Q2xvc2U=')].iloc[-1]
    expirations = tk.options
    if not expirations:
        sys.exit(f'{ticker}에 대한 옵션 만기 정보를 가져오지 못했습니다.')
    today = datetime.now(timezone.utc).date()
    rows = []
    for exp in expirations:
        exp_date = datetime.strptime(exp, _ρ('JVktJW0tJWQ=')).date()
        days = (exp_date - today).days
        if days < 0 or days > max_days:
            continue
        try:
            chain = tk.option_chain(exp)
        except Exception as e:
            print(f'  [경고] {exp} 만기 데이터 로드 실패: {e}', file=sys.stderr)
            continue
        T = max(days, 1) / 365.0
        calls = chain.calls.copy()
        calls[_ρ('dHlwZQ==')] = _ρ('Y2FsbA==')
        puts = chain.puts.copy()
        puts[_ρ('dHlwZQ==')] = _ρ('cHV0')
        for df in (calls, puts):
            df[_ρ('ZXhwaXJhdGlvbg==')] = exp
            df[_ρ('VA==')] = T
        rows.append(calls)
        rows.append(puts)
    if not rows:
        sys.exit(f'{max_days}일 이내 만기 옵션 데이터가 없습니다. --max-days 값을 늘려보세요.')
    full = pd.concat(rows, ignore_index=True)
    full = full[[_ρ('c3RyaWtl'), _ρ('dHlwZQ=='), _ρ('b3BlbkludGVyZXN0'), _ρ('aW1wbGllZFZvbGF0aWxpdHk='), _ρ('VA=='), _ρ('ZXhwaXJhdGlvbg==')]]
    full = full.dropna(subset=[_ρ('c3RyaWtl'), _ρ('b3BlbkludGVyZXN0'), _ρ('aW1wbGllZFZvbGF0aWxpdHk=')])
    full = full[(full[_ρ('b3BlbkludGVyZXN0')] > 0) & (full[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')] > 0)]
    return (full, float(spot))

def compute_gex_curve(chain: pd.DataFrame, spot: float, price_range_pct: float=0.15, n_points: int=39517 ^ _κ):
    calls = chain[chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')]
    puts = chain[chain[_ρ('dHlwZQ==')] == _ρ('cHV0')]
    price_grid = np.linspace(spot * (1 - price_range_pct), spot * (1 + price_range_pct), n_points)
    gex_values = []
    for S in price_grid:
        call_gamma = bs_gamma(S, calls[_ρ('c3RyaWtl')].values, calls[_ρ('VA==')].values, calls[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].values)
        put_gamma = bs_gamma(S, puts[_ρ('c3RyaWtl')].values, puts[_ρ('VA==')].values, puts[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].values)
        call_gex = np.sum(call_gamma * calls[_ρ('b3BlbkludGVyZXN0')].values) * (39488 ^ _κ) * S ** 2 * 0.01
        put_gex = np.sum(put_gamma * puts[_ρ('b3BlbkludGVyZXN0')].values) * (39488 ^ _κ) * S ** 2 * 0.01
        net_gex = call_gex - put_gex
        gex_values.append(net_gex)
    return (price_grid, np.array(gex_values))

def find_walls(chain: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp, grp in chain.groupby(_ρ('ZXhwaXJhdGlvbg==')):
        calls = grp[grp[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')]
        puts = grp[grp[_ρ('dHlwZQ==')] == _ρ('cHV0')]
        row = {_ρ('ZXhwaXJhdGlvbg=='): exp}
        if not calls.empty:
            top_call = calls.loc[calls[_ρ('b3BlbkludGVyZXN0')].idxmax()]
            row[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] = top_call[_ρ('c3RyaWtl')]
            row[_ρ('Y2FsbF93YWxsX29p')] = int(top_call[_ρ('b3BlbkludGVyZXN0')])
        else:
            row[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] = row[_ρ('Y2FsbF93YWxsX29p')] = None
        if not puts.empty:
            top_put = puts.loc[puts[_ρ('b3BlbkludGVyZXN0')].idxmax()]
            row[_ρ('cHV0X3dhbGxfc3RyaWtl')] = top_put[_ρ('c3RyaWtl')]
            row[_ρ('cHV0X3dhbGxfb2k=')] = int(top_put[_ρ('b3BlbkludGVyZXN0')])
        else:
            row[_ρ('cHV0X3dhbGxfc3RyaWtl')] = row[_ρ('cHV0X3dhbGxfb2k=')] = None
        rows.append(row)
    return pd.DataFrame(rows).sort_values(_ρ('ZXhwaXJhdGlvbg==')).reset_index(drop=True)

def find_walls_aggregate(chain: pd.DataFrame) -> dict:
    calls = chain[chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')].groupby(_ρ('c3RyaWtl'))[_ρ('b3BlbkludGVyZXN0')].sum()
    puts = chain[chain[_ρ('dHlwZQ==')] == _ρ('cHV0')].groupby(_ρ('c3RyaWtl'))[_ρ('b3BlbkludGVyZXN0')].sum()
    result = {}
    if not calls.empty:
        result[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] = float(calls.idxmax())
        result[_ρ('Y2FsbF93YWxsX29p')] = int(calls.max())
    if not puts.empty:
        result[_ρ('cHV0X3dhbGxfc3RyaWtl')] = float(puts.idxmax())
        result[_ρ('cHV0X3dhbGxfb2k=')] = int(puts.max())
    return result

def find_flip_point(price_grid, gex_values):
    sign = np.sign(gex_values)
    crossings = []
    for i in range(len(sign) - 1):
        if sign[i] == 0:
            crossings.append(price_grid[i])
        elif sign[i] != sign[i + 1]:
            x0, x1 = (price_grid[i], price_grid[i + 1])
            y0, y1 = (gex_values[i], gex_values[i + 1])
            crossings.append(x0 - y0 * (x1 - x0) / (y1 - y0))
    if len(price_grid) > 1:
        tol = abs(price_grid[1] - price_grid[0]) * 1e-06
        deduped = []
        for c in sorted(crossings):
            if not deduped or abs(c - deduped[-1]) > tol:
                deduped.append(c)
        return deduped
    return crossings

def load_futures_symbol(csv_path: str, symbol: str):
    df = pd.read_csv(csv_path)
    required = {_ρ('c3ltYm9s'), _ρ('c3RyaWtl'), _ρ('dHlwZQ=='), _ρ('b3BlbkludGVyZXN0'), _ρ('ZXhwaXJhdGlvbg=='), _ρ('c3BvdA=='), _ρ('Y29udHJhY3RfbXVsdGlwbGllcg==')}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f'CSV에 필요한 컬럼이 없습니다: {missing}. CSV 캡처 코드로 다시 캡처하세요.')
    for optional_col in (_ρ('aW1wbGllZFZvbGF0aWxpdHk='), _ρ('Z2FtbWFfYmFyY2hhcnQ='), _ρ('ZGVsdGFfYmFyY2hhcnQ=')):
        if optional_col not in df.columns:
            df[optional_col] = np.nan
    sub = df[df[_ρ('c3ltYm9s')] == symbol].copy()
    if sub.empty:
        available = sorted(df[_ρ('c3ltYm9s')].unique())
        sys.exit(f"'{symbol}' 심볼이 CSV에 없습니다. 사용 가능한 심볼: {available}")
    if sub[_ρ('c3BvdA==')].isna().any() or sub[_ρ('ZXhwaXJhdGlvbg==')].isna().any():
        sys.exit(f'{symbol}: spot 또는 expiration 값이 비어 있습니다. CSV 캡처 코드의 MANUAL_OVERRIDE를 채워서 다시 캡처하세요.')
    spot = float(sub[_ρ('c3BvdA==')].iloc[0])
    multiplier = float(sub[_ρ('Y29udHJhY3RfbXVsdGlwbGllcg==')].iloc[0])
    today = date.today()

    def days_to_expiry(exp_str):
        exp_date = datetime.strptime(str(exp_str), _ρ('JVktJW0tJWQ=')).date()
        return max((exp_date - today).days, 1)
    sub[_ρ('VA==')] = sub[_ρ('ZXhwaXJhdGlvbg==')].apply(lambda e: days_to_expiry(e) / 365.0)
    sub = sub.dropna(subset=[_ρ('c3RyaWtl'), _ρ('b3BlbkludGVyZXN0')])
    sub = sub[sub[_ρ('b3BlbkludGVyZXN0')] > 0]
    return (sub, spot, multiplier)

def compute_gex_curve_futures_bs(chain: pd.DataFrame, spot: float, multiplier: float, r: float, price_range_pct: float=0.15, n_points: int=39517 ^ _κ):
    calls = chain[(chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')) & chain[_ρ('aXZfZWZmZWN0aXZl')].notna() & (chain[_ρ('aXZfZWZmZWN0aXZl')] > 0)]
    puts = chain[(chain[_ρ('dHlwZQ==')] == _ρ('cHV0')) & chain[_ρ('aXZfZWZmZWN0aXZl')].notna() & (chain[_ρ('aXZfZWZmZWN0aXZl')] > 0)]
    price_grid = np.linspace(spot * (1 - price_range_pct), spot * (1 + price_range_pct), n_points)
    gex_values = []
    for S in price_grid:
        call_gamma = b76_gamma(S, calls[_ρ('c3RyaWtl')].values, calls[_ρ('VA==')].values, calls[_ρ('aXZfZWZmZWN0aXZl')].values, r)
        put_gamma = b76_gamma(S, puts[_ρ('c3RyaWtl')].values, puts[_ρ('VA==')].values, puts[_ρ('aXZfZWZmZWN0aXZl')].values, r)
        call_gex = np.sum(call_gamma * calls[_ρ('b3BlbkludGVyZXN0')].values) * multiplier * S ** 2 * 0.01
        put_gex = np.sum(put_gamma * puts[_ρ('b3BlbkludGVyZXN0')].values) * multiplier * S ** 2 * 0.01
        gex_values.append(call_gex - put_gex)
    return (price_grid, np.array(gex_values))

def compute_current_gex_from_barchart_gamma(chain: pd.DataFrame, spot: float, multiplier: float):
    calls = chain[(chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')) & chain[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].notna()]
    puts = chain[(chain[_ρ('dHlwZQ==')] == _ρ('cHV0')) & chain[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].notna()]
    call_gex = np.sum(calls[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].values * calls[_ρ('b3BlbkludGVyZXN0')].values) * multiplier * spot ** 2 * 0.01
    put_gex = np.sum(puts[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].values * puts[_ρ('b3BlbkludGVyZXN0')].values) * multiplier * spot ** 2 * 0.01
    return (call_gex - put_gex, len(calls), len(puts))

def find_walls_futures_raw(chain: pd.DataFrame) -> dict:
    calls = chain[chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')]
    puts = chain[chain[_ρ('dHlwZQ==')] == _ρ('cHV0')]
    result = {}
    if not calls.empty:
        top = calls.loc[calls[_ρ('b3BlbkludGVyZXN0')].idxmax()]
        result[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] = float(top[_ρ('c3RyaWtl')])
        result[_ρ('Y2FsbF93YWxsX29p')] = int(top[_ρ('b3BlbkludGVyZXN0')])
    if not puts.empty:
        top = puts.loc[puts[_ρ('b3BlbkludGVyZXN0')].idxmax()]
        result[_ρ('cHV0X3dhbGxfc3RyaWtl')] = float(top[_ρ('c3RyaWtl')])
        result[_ρ('cHV0X3dhbGxfb2k=')] = int(top[_ρ('b3BlbkludGVyZXN0')])
    return result

def find_walls_futures_smoothed(chain: pd.DataFrame, spot: float, bandwidth_pct: float=0.01, grid_points: int=39036 ^ _κ) -> dict:
    bandwidth = max(spot * bandwidth_pct, 1e-06)
    result = {}
    for opt_type, prefix in ((_ρ('Y2FsbA=='), _ρ('Y2FsbA==')), (_ρ('cHV0'), _ρ('cHV0'))):
        sub = chain[chain[_ρ('dHlwZQ==')] == opt_type]
        if sub.empty:
            continue
        strikes = sub[_ρ('c3RyaWtl')].values.astype(float)
        oi = sub[_ρ('b3BlbkludGVyZXN0')].values.astype(float)
        lo, hi = (strikes.min() - (39463 ^ _κ) * bandwidth, strikes.max() + (39463 ^ _κ) * bandwidth)
        grid = np.linspace(lo, hi, grid_points)
        weights = np.exp(-0.5 * ((grid[:, None] - strikes[None, :]) / bandwidth) ** 2)
        smoothed = weights @ oi
        peak_idx = int(np.argmax(smoothed))
        peak_level = float(grid[peak_idx])
        near_mask = np.abs(strikes - peak_level) <= bandwidth
        result[f'{prefix}_wall_strike'] = peak_level
        result[f'{prefix}_wall_region_oi'] = float(oi[near_mask].sum())
    return result
MONTHLY_OPTIONS_ROOT = {_ρ('TlE='): _ρ('TVEx'), _ρ('RVM='): _ρ('TVcx')}

def normalize_options_symbol(symbol: str, ticker: str | None) -> str | None:
    if not ticker:
        return ticker
    root = MONTHLY_OPTIONS_ROOT.get(symbol)
    if not root or ticker.startswith(root):
        return ticker
    if ticker.startswith(symbol) and len(ticker) > len(symbol):
        converted = root + ticker[len(symbol):]
        print(f'  [정보] {symbol}: 선물 심볼({ticker})을 옵션 시리즈 심볼({converted})로 변환')
        return converted
    return ticker

def extract_api_symbol_from_config(html: str) -> str | None:
    for m in re.finditer(_ρ('ZGF0YS1hcGktY29uZmlnPSIoW14iXSopIg=='), html):
        raw = html_module.unescape(m.group(1))
        try:
            cfg = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        api = cfg.get(_ρ('YXBp'), {})
        if api.get(_ρ('bWV0aG9k')) == _ρ('cXVvdGVz') and api.get(_ρ('bGlzdA==')) == _ρ('ZnV0dXJlcy5vcHRpb25z') and api.get(_ρ('c3ltYm9s')):
            return api[_ρ('c3ltYm9s')]
    return None

async def extract_page_meta(page, html: str, symbol: str | None=None) -> dict:
    meta = {}
    ticker_from_config = extract_api_symbol_from_config(html)
    m = re.search(_ρ('ImJjX3RpY2tlciJccyo6XHMqIihbXiJdKyki'), html)
    ticker_from_meta = m.group(1) if m else None
    ticker = ticker_from_config or ticker_from_meta
    if symbol:
        ticker = normalize_options_symbol(symbol, ticker)
    meta[_ρ('dGlja2Vy')] = ticker
    meta[_ρ('dGlja2VyX3NvdXJjZQ==')] = _ρ('ZGF0YS1hcGktY29uZmln') if ticker_from_config else _ρ('YmNfdGlja2Vy') if ticker_from_meta else None
    m = re.search(_ρ('PG1ldGFccytuYW1lPSJjc3JmLXRva2VuIlxzK2NvbnRlbnQ9IihbXiJdKyki'), html)
    meta[_ρ('Y3NyZl90b2tlbg==')] = m.group(1) if m else None
    xsrf_cookie = None
    try:
        for c in await page.context.cookies():
            if c.get(_ρ('bmFtZQ=='), '').upper() == _ρ('WFNSRi1UT0tFTg=='):
                from urllib.parse import unquote
                xsrf_cookie = unquote(c.get(_ρ('dmFsdWU='), ''))
                break
    except Exception:
        pass
    meta[_ρ('eHNyZl9jb29raWU=')] = xsrf_cookie
    return meta

async def try_direct_api(page, referer_url: str, meta: dict, symbol: str) -> tuple:
    if not meta.get(_ρ('dGlja2Vy')):
        return (None, _ρ('KGJjX3RpY2tlcuulvCDtjpjsnbTsp4Dsl5DshJwg66q7IOywvuyVhCDsp4HsoJEg7Zi47Lac7J2EIOyLnOuPhO2VmOyngCDslYrsnYwp'))
    headers = {_ρ('QWNjZXB0'): _ρ('YXBwbGljYXRpb24vanNvbiwgdGV4dC9wbGFpbiwgKi8q'), _ρ('WC1SZXF1ZXN0ZWQtV2l0aA=='): _ρ('WE1MSHR0cFJlcXVlc3Q='), _ρ('UmVmZXJlcg=='): referer_url}
    if meta.get(_ρ('Y3NyZl90b2tlbg==')):
        headers[_ρ('WC1DU1JGLVRPS0VO')] = meta[_ρ('Y3NyZl90b2tlbg==')]
    if meta.get(_ρ('eHNyZl9jb29raWU=')):
        headers[_ρ('WC1YU1JGLVRPS0VO')] = meta[_ρ('eHNyZl9jb29raWU=')]
    params = {_ρ('c3ltYm9s'): meta[_ρ('dGlja2Vy')], _ρ('bGlzdA=='): _ρ('ZnV0dXJlcy5vcHRpb25z'), _ρ('ZmllbGRz'): CAPTURE_API_FIELDS, _ρ('bWV0YQ=='): _ρ('ZmllbGQuc2hvcnROYW1lLGZpZWxkLmRlc2NyaXB0aW9uLGZpZWxkLnR5cGU='), _ρ('Z3JvdXBCeQ=='): _ρ('b3B0aW9uVHlwZQ=='), _ρ('b3JkZXJCeQ=='): _ρ('c3RyaWtl'), _ρ('b3JkZXJEaXI='): _ρ('YXNj'), _ρ('cmF3'): _ρ('MQ==')}
    try:
        resp = await page.request.get(CAPTURE_API_URL, params=params, headers=headers, timeout=54276 ^ _κ)
        return (resp.status, await resp.text())
    except Exception as e:
        return (None, f'(요청 실패: {e})')

def guess_spot(html: str) -> float | None:
    m = re.search(_ρ('Imxhc3RQcmljZSJccyo6XHMqIj8oW1xkLF0rXC4/XGQqKSI/'), html)
    if m:
        return float(m.group(1).replace(_ρ('LA=='), ''))
    m = re.search(_ρ('ZGF0YS1uZy1ub24tYmluZGFibGVbXj5dKj5ccyooW1xkLF17Myx9XC5cZHsyfSlccyo8'), html)
    if m:
        return float(m.group(1).replace(_ρ('LA=='), ''))
    m = re.search(_ρ('TGFzdFxzKlByaWNlW14wLTldezAsMjB9KFtcZCxdezMsfVwuP1xkezAsMn0p'), html, re.I)
    if m:
        return float(m.group(1).replace(_ρ('LA=='), ''))
    return None

def guess_expiration(html: str) -> str | None:
    m = re.search(_ρ('ZXhwaXJhdGlvbiBvblxzKig/OjxbXj5dKj5ccyopKihcZHsyfSkvKFxkezJ9KS8oXGR7Mn0p'), html, re.I)
    if m:
        mm, dd, yy = m.groups()
        try:
            return datetime.strptime(f'20{yy}-{mm}-{dd}', _ρ('JVktJW0tJWQ=')).date().isoformat()
        except ValueError:
            pass
    m = re.search(_ρ('KFtBLVpdW2Etel17Mn1ccytcZHsxLDJ9LFxzKjIwXGR7Mn0p'), html)
    if m:
        try:
            return datetime.strptime(m.group(1), _ρ('JWIgJWQsICVZ')).date().isoformat()
        except ValueError:
            pass
    return None

def _find_candidate_lists(obj, path=''):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.extend(_find_candidate_lists(v, f'{path}.{k}'))
    elif isinstance(obj, list):
        if obj and all((isinstance(x, dict) for x in obj)):
            found.append((path, obj))
        for i, x in enumerate(obj[:39446 ^ _κ]):
            found.extend(_find_candidate_lists(x, f'{path}[{i}]'))
    return found

def _score_candidate(records) -> int:
    if not records:
        return -1
    keys = set()
    for r in records[:39457 ^ _κ]:
        keys.update((str(k).lower() for k in r.keys()))
    score = 0
    if any((_ρ('c3RyaWtl') in k for k in keys)):
        score += 39463 ^ _κ
    if any((_ρ('b3Blbg==') in k and _ρ('aW50') in k or re.search(_ρ('XGJvaVxi'), k) for k in keys)):
        score += 2
    if any((_ρ('aW1wbA==') in k and _ρ('dm9s') in k or re.search(_ρ('XGJpdlxi'), k) for k in keys)):
        score += 2
    if any((_ρ('Y2FsbA==') in k for k in keys)) or any((_ρ('cHV0') in k for k in keys)):
        score += 1
    return score

def _to_float(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == '' or s.upper() in (_ρ('Tk9ORQ=='), _ρ('TlVMTA=='), _ρ('LQ=='), _ρ('Ti9B'), _ρ('TkE=')):
        return None
    s = s.replace(_ρ('LA=='), '').replace(_ρ('JQ=='), '')
    m = re.match(_ρ('Xi0/XGQrXC4/XGQq'), s)
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
    has_prefixed = any((re.search(_ρ('XmNhbGw='), k, re.I) for k in sample_keys)) and any((re.search(_ρ('XnB1dA=='), k, re.I) for k in sample_keys))
    rows = []
    if has_prefixed:
        for r in records:
            strike = _to_float(_get_field(r, _ρ('c3RyaWtl')))
            if strike is None:
                continue
            call_oi = _to_float(_get_field(r, _ρ('Y2FsbC4qb3Blbi4qaW50fGNhbGwuKlxib2lcYg==')))
            call_iv = _normalize_iv(_to_float(_get_field(r, _ρ('Y2FsbC4qKGltcGwuKnZvbHxcYml2XGIp'))))
            put_oi = _to_float(_get_field(r, _ρ('cHV0LipvcGVuLippbnR8cHV0LipcYm9pXGI=')))
            put_iv = _normalize_iv(_to_float(_get_field(r, _ρ('cHV0LiooaW1wbC4qdm9sfFxiaXZcYik='))))
            if call_oi is not None:
                rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): _ρ('Y2FsbA=='), _ρ('b3BlbkludGVyZXN0'): call_oi, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): call_iv})
            if put_oi is not None:
                rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): _ρ('cHV0'), _ρ('b3BlbkludGVyZXN0'): put_oi, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): put_iv})
    else:
        for r in records:
            strike = _to_float(_get_field(r, _ρ('c3RyaWtl')))
            if strike is None:
                continue
            side_raw = _get_field(r, _ρ('Xih0eXBlfHNpZGV8cHV0ID9jYWxsfG9wdGlvbiA/dHlwZSkk'))
            side = str(side_raw).lower() if side_raw is not None else ''
            opt_type = _ρ('Y2FsbA==') if side[:1] == _ρ('Yw==') else _ρ('cHV0') if side[:1] == _ρ('cA==') else None
            oi = _to_float(_get_field(r, _ρ('b3Blbi4qaW50fFxib2lcYg==')))
            iv = _normalize_iv(_to_float(_get_field(r, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))))
            if opt_type is not None and oi is not None:
                rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): opt_type, _ρ('b3BlbkludGVyZXN0'): oi, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): iv})
    return rows

def _find_call_put_groups(obj, path=''):
    found = []
    if isinstance(obj, dict):
        keys_lower = {str(k).lower(): k for k in obj.keys()}
        call_key = next((keys_lower[k] for k in keys_lower if k in (_ρ('Y2FsbA=='), _ρ('Y2FsbHM='))), None)
        put_key = next((keys_lower[k] for k in keys_lower if k in (_ρ('cHV0'), _ρ('cHV0cw=='))), None)
        if call_key and put_key:
            call_list = obj[call_key]
            put_list = obj[put_key]
            if isinstance(call_list, list) and call_list and all((isinstance(x, dict) for x in call_list)) and isinstance(put_list, list) and put_list and all((isinstance(x, dict) for x in put_list)):
                found.append((f'{path}.{{{call_key}/{put_key}}}', call_list, put_list))
        for k, v in obj.items():
            found.extend(_find_call_put_groups(v, f'{path}.{k}'))
    elif isinstance(obj, list):
        for i, x in enumerate(obj[:39446 ^ _κ]):
            found.extend(_find_call_put_groups(x, f'{path}[{i}]'))
    return found

def _build_rows_from_grouped(call_records: list, put_records: list) -> list:
    rows = []
    for records, opt_type in ((call_records, _ρ('Y2FsbA==')), (put_records, _ρ('cHV0'))):
        for r in records:
            strike = _to_float(_get_field(r, _ρ('c3RyaWtl')))
            if strike is None:
                continue
            oi = _to_float(_get_field(r, _ρ('b3Blbi4qaW50fFxib2lcYg==')))
            iv = _normalize_iv(_to_float(_get_field(r, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))))
            delta = _to_float(_get_field(r, _ρ('XmRlbHRhJA==')))
            gamma = _to_float(_get_field(r, _ρ('XmdhbW1hJA==')))
            theta = _to_float(_get_field(r, _ρ('XnRoZXRhJA==')))
            vega = _to_float(_get_field(r, _ρ('XnZlZ2Ek')))
            if oi is not None:
                rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): opt_type, _ρ('b3BlbkludGVyZXN0'): oi, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): iv, _ρ('ZGVsdGFfYmFyY2hhcnQ='): delta, _ρ('Z2FtbWFfYmFyY2hhcnQ='): gamma, _ρ('dGhldGFfYmFyY2hhcnQ='): theta, _ρ('dmVnYV9iYXJjaGFydA=='): vega})
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
            if score >= 39457 ^ _κ and (flat_best is None or score > flat_best[0]):
                flat_best = (score, url, path, records)
    if grouped_best is not None:
        score, url, path, call_records, put_records = grouped_best
        dprint(f'  [디버그] Call/Put 분리 구조 채택: {url}  경로={path}  점수={score}  콜 {len(call_records)}행 / 풋 {len(put_records)}행')
        dprint(f'  [디버그] 콜 레코드 키: {list(call_records[0].keys())}')
        rows = _build_rows_from_grouped(call_records, put_records)
        if rows:
            return pd.DataFrame(rows)
        dprint(_ρ('ICBb65SU67KE6re4XSBDYWxsL1B1dCDqtazsobDsl5DshJwg7ZaJ7J2EIOuquyDrp4zrk6Yg4oaSIOuMgOyytCDqtazsobAg7Iuc64+ELg=='))
    if flat_best is None:
        dprint(f'  [디버그] JSON 응답 {len(captured)}개를 스캔했지만 옵션체인으로 보이는 데이터를 못 찾음.')
        return pd.DataFrame()
    score, url, path, records = flat_best
    dprint(f'  [디버그] JSON 후보 채택(단일 리스트): {url}  경로={path}  점수={score}  레코드수={len(records)}')
    dprint(f'  [디버그] 첫 레코드 키: {list(records[0].keys())}')
    rows = _build_rows_from_records(records)
    return pd.DataFrame(rows)

def parse_from_html_table(html: str) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        dprint(_ρ('ICBb65SU67KE6re4XSBIVE1M7JeQ7IScIDx0YWJsZT4g7YOc6re466W8IOyVhOyYiCDssL7sp4Ag66q77ZWoIChKUyDqt7jrpqzrk5zroZwg66CM642U66eB65CcIO2OmOydtOyngOydvCDqsIDriqXshLEg64aS7J2MKS4='))
        return pd.DataFrame()
    dprint(f'  [디버그] 페이지에서 표 {len(tables)}개 발견. 각 표의 shape: {[t.shape for t in tables]}')
    target = None
    for t in tables:
        cols = [str(c) for c in t.columns]
        if any((re.search(_ρ('c3RyaWtl'), c, re.I) for c in cols)):
            target = t
            break
    if target is None:
        return pd.DataFrame()
    cols = [str(c) for c in target.columns]
    strike_idx = next((i for i, c in enumerate(cols) if re.search(_ρ('c3RyaWtl'), c, re.I)))
    left = target.iloc[:, :strike_idx]
    strike_col = target.iloc[:, strike_idx]
    right = target.iloc[:, strike_idx + 1:]

    def find_col(block: pd.DataFrame, pattern: str):
        for c in block.columns:
            if re.search(pattern, str(c), re.I):
                return block[c]
        return None
    call_oi = find_col(left, _ρ('b3BlblxzKmludA=='))
    call_iv = find_col(left, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))
    put_oi = find_col(right, _ρ('b3BlblxzKmludA=='))
    put_iv = find_col(right, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))
    if call_oi is None or put_oi is None:
        return pd.DataFrame()

    def clean_num(s):
        return pd.to_numeric(s.astype(str).str.replace(_ρ('LA=='), '').str.replace(_ρ('JQ=='), '').str.strip(), errors=_ρ('Y29lcmNl'))
    rows = []
    strikes = clean_num(strike_col)
    call_oi_c, put_oi_c = (clean_num(call_oi), clean_num(put_oi))
    call_iv_c = clean_num(call_iv) if call_iv is not None else None
    put_iv_c = clean_num(put_iv) if put_iv is not None else None
    for i in range(len(target)):
        k = strikes.iloc[i]
        if pd.isna(k):
            continue
        if not pd.isna(call_oi_c.iloc[i]):
            rows.append({_ρ('c3RyaWtl'): k, _ρ('dHlwZQ=='): _ρ('Y2FsbA=='), _ρ('b3BlbkludGVyZXN0'): call_oi_c.iloc[i], _ρ('aW1wbGllZFZvbGF0aWxpdHk='): call_iv_c.iloc[i] / 100.0 if call_iv_c is not None else None})
        if not pd.isna(put_oi_c.iloc[i]):
            rows.append({_ρ('c3RyaWtl'): k, _ρ('dHlwZQ=='): _ρ('cHV0'), _ρ('b3BlbkludGVyZXN0'): put_oi_c.iloc[i], _ρ('aW1wbGllZFZvbGF0aWxpdHk='): put_iv_c.iloc[i] / 100.0 if put_iv_c is not None else None})
    return pd.DataFrame(rows)

def _finalize_capture_df(df: pd.DataFrame, html: str, symbol: str, cfg: dict, api_debug_text: str) -> pd.DataFrame:
    if df.empty:
        dprint(_ρ('ICBb65SU67KE6re4XSBIVE1MIDx0YWJsZT4g67Cp7Iud7Jy866GcIOyerOyLnOuPhC4='))
        df = parse_from_html_table(html)
    if df.empty:
        debug_path = f'barchart_debug_{symbol}.html'
        with open(debug_path, _ρ('dw=='), encoding=_ρ('dXRmLTg=')) as f:
            f.write(html)
        api_debug_path = f'barchart_api_{symbol}.txt'
        with open(api_debug_path, _ρ('dw=='), encoding=_ρ('dXRmLTg=')) as f:
            f.write(api_debug_text or '')
        print(f'  [경고] {symbol}: 옵션 데이터를 전혀 못 찾았습니다.')
        return df
    override = MANUAL_OVERRIDE.get(symbol, {})
    spot = override.get(_ρ('c3BvdA==')) or guess_spot(html)
    expiration = override.get(_ρ('ZXhwaXJhdGlvbg==')) or guess_expiration(html)
    print(f'  [결과] spot 추정값: {spot} | 만기 추정값: {expiration} | 옵션 {len(df)}행')
    if spot is None or expiration is None:
        print(f"  [주의] {symbol}: spot 또는 만기를 자동으로 못 찾았습니다. MANUAL_OVERRIDE['{symbol}'] = {{'spot': ..., 'expiration': 'YYYY-MM-DD'}} 로 채운 뒤 다시 실행하세요.")
    n_total = len(df)
    n_iv = int(df[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].notna().sum()) if _ρ('aW1wbGllZFZvbGF0aWxpdHk=') in df.columns else 0
    n_gamma = int(df[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].notna().sum()) if _ρ('Z2FtbWFfYmFyY2hhcnQ=') in df.columns else 0
    print(f'  [진단] IV 있는 행: {n_iv}/{n_total} | bcdb 자체 gamma 있는 행: {n_gamma}/{n_total}')
    df[_ρ('c3ltYm9s')] = symbol
    df[_ρ('c3BvdA==')] = spot
    df[_ρ('ZXhwaXJhdGlvbg==')] = expiration
    df[_ρ('Y29udHJhY3RfbXVsdGlwbGllcg==')] = cfg[_ρ('bXVsdGlwbGllcg==')]
    df = df.dropna(subset=[_ρ('b3BlbkludGVyZXN0')])
    df = df[df[_ρ('b3BlbkludGVyZXN0')] > 0]
    return df

def capture_one_requests(symbol: str, cfg: dict) -> pd.DataFrame:
    print(f'\n=== {symbol} 캡처 중 (requests, 브라우저 없음) ===')
    s = requests.Session()
    s.headers.update({_ρ('VXNlci1BZ2VudA=='): _ρ('TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wIFNhZmFyaS81MzcuMzY='), _ρ('QWNjZXB0LUxhbmd1YWdl'): _ρ('ZW4tVVMsZW47cT0wLjk=')})
    try:
        r = s.get(cfg[_ρ('dXJs')], timeout=39472 ^ _κ)
        html = r.text
    except Exception as e:
        dprint(f'  [디버그] 페이지 GET 실패: {e}')
        return pd.DataFrame()
    ticker = extract_api_symbol_from_config(html)
    if not ticker:
        m = re.search(_ρ('ImJjX3RpY2tlciJccyo6XHMqIihbXiJdKyki'), html)
        ticker = m.group(1) if m else None
    ticker = normalize_options_symbol(symbol, ticker)
    if ticker and _ρ('Kg==') in ticker:
        print(f'  [경고] {symbol}: 심볼이 안 풀린 채로 옴({ticker!r}). Barchart의 최근월물 별칭(*0) 처리 방식이 바뀐 것으로 보입니다 — TARGETS의 url을 만기 코드가 직접 박힌 형태(예: NQU26/options/MQ1U26)로 되돌려야 할 수 있습니다.')
    elif ticker:
        print(f'  [확인] {symbol}: 이번 캡처에 사용된 실제 계약 심볼 = {ticker}')
    m = re.search(_ρ('PG1ldGFccytuYW1lPSJjc3JmLXRva2VuIlxzK2NvbnRlbnQ9IihbXiJdKyki'), html)
    csrf_token = m.group(1) if m else None
    xsrf_cookie = None
    for name, value in s.cookies.items():
        if name.upper() == _ρ('WFNSRi1UT0tFTg=='):
            from urllib.parse import unquote
            xsrf_cookie = unquote(value)
            break
    dprint(f'  [디버그] 페이지에서 추출한 메타: ticker={ticker} csrf_token={('있음' if csrf_token else '없음')} xsrf_cookie={('있음' if xsrf_cookie else '없음')}')
    df = pd.DataFrame()
    if ticker and csrf_token and xsrf_cookie:
        dprint(_ρ('ICBb65SU67KE6re4XSBxdW90ZXMvZ2V0IOyXlOuTnO2PrOyduO2KuCDsp4HsoJEg7Zi47LacIOyLnOuPhCAocmVxdWVzdHMpLi4u'))
        headers = {_ρ('QWNjZXB0'): _ρ('YXBwbGljYXRpb24vanNvbiwgdGV4dC9wbGFpbiwgKi8q'), _ρ('WC1SZXF1ZXN0ZWQtV2l0aA=='): _ρ('WE1MSHR0cFJlcXVlc3Q='), _ρ('UmVmZXJlcg=='): cfg[_ρ('dXJs')], _ρ('WC1DU1JGLVRPS0VO'): csrf_token, _ρ('WC1YU1JGLVRPS0VO'): xsrf_cookie}
        params = {_ρ('c3ltYm9s'): ticker, _ρ('bGlzdA=='): _ρ('ZnV0dXJlcy5vcHRpb25z'), _ρ('ZmllbGRz'): CAPTURE_API_FIELDS, _ρ('bWV0YQ=='): _ρ('ZmllbGQuc2hvcnROYW1lLGZpZWxkLmRlc2NyaXB0aW9uLGZpZWxkLnR5cGU='), _ρ('Z3JvdXBCeQ=='): _ρ('b3B0aW9uVHlwZQ=='), _ρ('b3JkZXJCeQ=='): _ρ('c3RyaWtl'), _ρ('b3JkZXJEaXI='): _ρ('YXNj'), _ρ('cmF3'): _ρ('MQ==')}
        try:
            r2 = s.get(CAPTURE_API_URL, params=params, headers=headers, timeout=39472 ^ _κ)
            api_debug_text = f'status={r2.status_code}\n\n{r2.text}'
            if r2.status_code == 39660 ^ _κ and r2.text:
                dprint(f'  [디버그] 직접 호출 응답 status=200, 길이={len(r2.text)}자.')
                df = parse_from_json_candidates([(CAPTURE_API_URL, r2.text)])
            else:
                dprint(f'  [디버그] 직접 호출 실패: status={r2.status_code}, 미리보기: {r2.text[:300]!r}')
        except Exception as e:
            api_debug_text = f'(요청 실패: {e})'
            dprint(f'  [디버그] 직접 호출 예외: {e}')
    else:
        api_debug_text = _ρ('KGNzcmZfdG9rZW4veHNyZl9jb29raWUvdGlja2VyIOykkSDtlZjrgpjrpbwg66q7IOywvuyVhCBBUEkg7Zi47Lac7J2EIOyDneuete2VqCk=')
        dprint(f'  [디버그] {api_debug_text}')
    return _finalize_capture_df(df, html, symbol, cfg, api_debug_text)

async def capture_one(symbol: str, cfg: dict, async_playwright) -> pd.DataFrame:
    print(f'\n=== {symbol} 캡처 중 ===')
    df = pd.DataFrame()
    html = ''
    api_debug_text = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=_ρ('TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wIFNhZmFyaS81MzcuMzY='))
        captured_json = []

        async def on_response(response):
            try:
                ct = response.headers.get(_ρ('Y29udGVudC10eXBl'), '')
                if _ρ('anNvbg==') not in ct.lower():
                    return
                body = await response.text()
                if len(body) > MAX_BODY_BYTES:
                    return
                if re.search(_ρ('c3RyaWtl'), body, re.I):
                    captured_json.append((response.url, body))
            except Exception:
                pass
        page.on(_ρ('cmVzcG9uc2U='), on_response)
        await page.goto(cfg[_ρ('dXJs')], wait_until=_ρ('ZG9tY29udGVudGxvYWRlZA=='), timeout=13804 ^ _κ)
        await page.wait_for_timeout(40436 ^ _κ)
        html = await page.content()
        meta = await extract_page_meta(page, html, symbol)
        dprint(f'  [디버그] 페이지에서 추출한 메타: ticker={meta.get('ticker')} (출처: {meta.get('ticker_source')}) csrf_token={('있음' if meta.get('csrf_token') else '없음')} xsrf_cookie={('있음' if meta.get('xsrf_cookie') else '없음')}')
        _ticker = meta.get(_ρ('dGlja2Vy'))
        if _ticker and _ρ('Kg==') in _ticker:
            print(f'  [경고] {symbol}: 심볼이 안 풀린 채로 옴({_ticker!r}). Barchart의 최근월물 별칭(*0) 처리 방식이 바뀐 것으로 보입니다 — TARGETS의 url을 만기 코드가 직접 박힌 형태로 되돌려야 할 수 있습니다.')
        elif _ticker:
            print(f'  [확인] {symbol}: 이번 캡처에 사용된 실제 계약 심볼 = {_ticker}')
        dprint(_ρ('ICBb65SU67KE6re4XSAx64uo6rOEOiBxdW90ZXMvZ2V0IOyXlOuTnO2PrOyduO2KuCDsp4HsoJEg7Zi47LacIOyLnOuPhC4uLg=='))
        status, body = await try_direct_api(page, cfg[_ρ('dXJs')], meta, symbol)
        api_debug_text = f'status={status}\n\n{(body if body else '')}'
        if status == 39660 ^ _κ and body:
            dprint(f'  [디버그] 직접 호출 응답 status=200, 길이={len(body)}자.')
            df = parse_from_json_candidates([(CAPTURE_API_URL, body)])
        else:
            dprint(f'  [디버그] 직접 호출 실패 또는 빈 응답: status={status}, 내용 미리보기: {str(body)[:300]!r}')
        if df.empty:
            dprint(f'  [디버그] 2단계: 페이지 로드 중 가로챈 JSON 응답 {len(captured_json)}개 스캔')
            df = parse_from_json_candidates(captured_json)
        await browser.close()
    return _finalize_capture_df(df, html, symbol, cfg, api_debug_text)

def write_or_merge_futures_csv(csv_path: str, new_frames_by_symbol: dict) -> pd.DataFrame | None:
    existing = None
    if os.path.exists(csv_path):
        try:
            existing = pd.read_csv(csv_path)
        except Exception as e:
            print(f'  [경고] 기존 CSV 읽기 실패, 새로 씀: {e}')
    frames = []
    captured_symbols = set(new_frames_by_symbol.keys())
    if existing is not None and (not existing.empty) and (_ρ('c3ltYm9s') in existing.columns):
        frames.append(existing[~existing[_ρ('c3ltYm9s')].isin(captured_symbols)])
    for df in new_frames_by_symbol.values():
        if df is not None and (not df.empty):
            frames.append(df)
    if not frames or all((f.empty for f in frames)):
        return None
    full = pd.concat(frames, ignore_index=True)
    for c in FUTURES_CSV_COLUMNS:
        if c not in full.columns:
            full[c] = None
    full = full[FUTURES_CSV_COLUMNS]
    full.to_csv(csv_path, index=False)
    return full

def _build_greeks_rows(records: list) -> list:
    rows = []
    for r in records:
        strike = _to_float(_get_field(r, _ρ('c3RyaWtl')))
        if strike is None:
            continue
        side_raw = _get_field(r, _ρ('Xih0eXBlfHNpZGV8cHV0ID9jYWxsfG9wdGlvbiA/dHlwZSkk'))
        side = str(side_raw).lower() if side_raw is not None else ''
        opt_type = _ρ('Y2FsbA==') if side[:1] == _ρ('Yw==') else _ρ('cHV0') if side[:1] == _ρ('cA==') else None
        if opt_type is None:
            continue
        iv = _normalize_iv(_to_float(_get_field(r, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))))
        delta = _to_float(_get_field(r, _ρ('XmRlbHRhJA==')))
        gamma = _to_float(_get_field(r, _ρ('XmdhbW1hJA==')))
        theta = _to_float(_get_field(r, _ρ('XnRoZXRhJA==')))
        vega = _to_float(_get_field(r, _ρ('XnZlZ2Ek')))
        if iv is None and delta is None and (gamma is None):
            continue
        rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): opt_type, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): iv, _ρ('ZGVsdGFfYmFyY2hhcnQ='): delta, _ρ('Z2FtbWFfYmFyY2hhcnQ='): gamma, _ρ('dGhldGFfYmFyY2hhcnQ='): theta, _ρ('dmVnYV9iYXJjaGFydA=='): vega})
    return rows

def _build_greeks_rows_from_grouped(call_records: list, put_records: list) -> list:
    rows = []
    for records, opt_type in ((call_records, _ρ('Y2FsbA==')), (put_records, _ρ('cHV0'))):
        for r in records:
            strike = _to_float(_get_field(r, _ρ('c3RyaWtl')))
            if strike is None:
                continue
            iv = _normalize_iv(_to_float(_get_field(r, _ρ('aW1wbC4qdm9sfFxiaXZcYg=='))))
            delta = _to_float(_get_field(r, _ρ('XmRlbHRhJA==')))
            gamma = _to_float(_get_field(r, _ρ('XmdhbW1hJA==')))
            theta = _to_float(_get_field(r, _ρ('XnRoZXRhJA==')))
            vega = _to_float(_get_field(r, _ρ('XnZlZ2Ek')))
            if iv is None and delta is None and (gamma is None):
                continue
            rows.append({_ρ('c3RyaWtl'): strike, _ρ('dHlwZQ=='): opt_type, _ρ('aW1wbGllZFZvbGF0aWxpdHk='): iv, _ρ('ZGVsdGFfYmFyY2hhcnQ='): delta, _ρ('Z2FtbWFfYmFyY2hhcnQ='): gamma, _ρ('dGhldGFfYmFyY2hhcnQ='): theta, _ρ('dmVnYV9iYXJjaGFydA=='): vega})
    return rows

def parse_greeks_from_json_candidates(captured: list) -> pd.DataFrame:
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
            if score >= 39457 ^ _κ and (flat_best is None or score > flat_best[0]):
                flat_best = (score, url, path, records)
    if grouped_best is not None:
        score, url, path, call_records, put_records = grouped_best
        dprint(f'  [디버그-그릭스] Call/Put 분리 구조 채택: {url}  경로={path}  점수={score}')
        rows = _build_greeks_rows_from_grouped(call_records, put_records)
        if rows:
            return pd.DataFrame(rows)
        dprint(_ρ('ICBb65SU67KE6re4Leq3uOumreyKpF0gQ2FsbC9QdXQg6rWs7KGw7JeQ7IScIO2WieydhCDrqrsg66eM65OmIOKGkiDrjIDssrQg6rWs7KGwIOyLnOuPhC4='))
    if flat_best is None:
        dprint(f'  [디버그-그릭스] JSON 응답 {len(captured)}개를 스캔했지만 그릭스 데이터를 못 찾음.')
        return pd.DataFrame()
    score, url, path, records = flat_best
    dprint(f'  [디버그-그릭스] JSON 후보 채택(단일 리스트): {url}  경로={path}  점수={score}  레코드수={len(records)}')
    dprint(f'  [디버그-그릭스] 첫 레코드 키: {list(records[0].keys())}')
    rows = _build_greeks_rows(records)
    return pd.DataFrame(rows)

async def capture_greeks_one(symbol: str, cfg: dict, async_playwright) -> pd.DataFrame:
    print(f'\n=== {symbol} Volatility & Greeks 캡처 중 ===')
    captured_json = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=_ρ('TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wIFNhZmFyaS81MzcuMzY='))

        async def on_response(response):
            try:
                ct = response.headers.get(_ρ('Y29udGVudC10eXBl'), '')
                if _ρ('anNvbg==') not in ct.lower():
                    return
                body = await response.text()
                if len(body) > MAX_BODY_BYTES:
                    return
                if re.search(_ρ('c3RyaWtl'), body, re.I):
                    captured_json.append((response.url, body))
            except Exception:
                pass
        page.on(_ρ('cmVzcG9uc2U='), on_response)
        try:
            await page.goto(cfg[_ρ('dXJs')], wait_until=_ρ('ZG9tY29udGVudGxvYWRlZA=='), timeout=13804 ^ _κ)
            await page.wait_for_timeout(40436 ^ _κ)
        except Exception as e:
            print(f'  [오류] {symbol} Greeks 페이지 로드 실패: {e}')
            await browser.close()
            return pd.DataFrame()
        await browser.close()
    df = parse_greeks_from_json_candidates(captured_json)
    n_iv = int(df[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].notna().sum()) if not df.empty and _ρ('aW1wbGllZFZvbGF0aWxpdHk=') in df.columns else 0
    print(f'  [결과] Greeks {len(df)}행 확보 (IV 있는 행 {n_iv}개)')
    return df

def _merge_greeks(df_main: pd.DataFrame, df_greeks: pd.DataFrame) -> pd.DataFrame:
    if df_greeks is None or df_greeks.empty:
        return df_main
    greek_cols = [_ρ('c3RyaWtl'), _ρ('dHlwZQ=='), _ρ('aW1wbGllZFZvbGF0aWxpdHk='), _ρ('ZGVsdGFfYmFyY2hhcnQ='), _ρ('Z2FtbWFfYmFyY2hhcnQ='), _ρ('dGhldGFfYmFyY2hhcnQ='), _ρ('dmVnYV9iYXJjaGFydA==')]
    df_greeks = df_greeks[[c for c in greek_cols if c in df_greeks.columns]]
    merged = df_main.drop(columns=[c for c in greek_cols if c != _ρ('c3RyaWtl') and c != _ρ('dHlwZQ==') and (c in df_main.columns)]).merge(df_greeks, on=[_ρ('c3RyaWtl'), _ρ('dHlwZQ==')], how=_ρ('bGVmdA=='))
    return merged

def run_capture_sync(symbols: list, csv_path: str):
    results = {}
    need_playwright_retry = []
    for sym in symbols:
        cfg = TARGETS[sym]
        try:
            df = capture_one_requests(sym, cfg)
        except Exception as e:
            print(f'  [오류] {sym} requests 캡처 실패: {e}')
            df = pd.DataFrame()
        if df.empty:
            need_playwright_retry.append(sym)
        else:
            results[sym] = df
    if need_playwright_retry:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print(f'  [경고] requests 방식으로 못 받은 심볼: {need_playwright_retry}. playwright가 설치돼 있지 않아 재시도를 건너뜁니다 (설치: pip install playwright && playwright install --with-deps chromium).')
        else:
            print(f'  [정보] requests 방식으로 못 받은 심볼 {need_playwright_retry}을 Playwright로 재시도합니다...')

            async def _run():
                out = {}
                for sym in need_playwright_retry:
                    cfg = TARGETS[sym]
                    try:
                        out[sym] = await capture_one(sym, cfg, async_playwright)
                    except Exception as e:
                        print(f'  [오류] {sym} Playwright 캡처 실패: {e}')
                        out[sym] = pd.DataFrame()
                return out
            try:
                pw_results = asyncio.run(_run())
            except RuntimeError:
                import nest_asyncio
                nest_asyncio.apply()
                pw_results = asyncio.get_event_loop().run_until_complete(_run())
            results.update(pw_results)
    symbols_with_data = [s for s in symbols if s in results and (not results[s].empty)]
    if symbols_with_data:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print(_ρ('ICBb7KCV67O0XSBwbGF5d3JpZ2h06rCAIOyXhuyWtCBHcmVla3MoSVYv64247YOAL+qwkOuniCkg67OR7ZWp7J2AIOqxtOuEiOucgeuLiOuLpCAoT0kg6riw67CYIOy9nOyblC/tkovsm5Qg67aE7ISd7J2AIOqzhOyGjSDqsIDriqUpLg=='))
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
                        print(f'  [오류] {sym} Greeks 캡처 실패: {e}')
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
                n_iv = int(results[sym][_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].notna().sum())
                print(f'  [병합 완료] {sym}: IV 있는 행 {n_iv}/{len(results[sym])}')
    full = write_or_merge_futures_csv(csv_path, results)
    if full is None:
        sys.exit(_ρ('7Lqh7LKY65CcIOuNsOydtO2EsOqwgCDsl4bsirXri4jri6QuIOychCBb65SU67KE6re4XS9b6rK96rOgXSDroZzqt7jrpbwg7ZmV7J247ZW07KO87IS47JqULg=='))
    print(f'\n[캡처 완료] CSV 저장/갱신됨 (전체 {len(full)}행)')
    print(full.groupby(_ρ('c3ltYm9s')).size())

def run_futures_mode(args):
    symbol = FUTURES_TICKER_ALIASES[args.ticker.strip().upper()]
    csv_has_symbol = False
    if os.path.exists(args.futures_csv):
        try:
            existing_symbols = set(pd.read_csv(args.futures_csv, usecols=[_ρ('c3ltYm9s')])[_ρ('c3ltYm9s')].unique())
            csv_has_symbol = symbol in existing_symbols
        except Exception as e:
            print(f'  [경고] 기존 CSV 확인 실패, 새로 캡처합니다: {e}')
    need_capture = args.recapture or not csv_has_symbol
    if need_capture:
        if args.no_capture:
            sys.exit(f'{symbol} 데이터가 없습니다. --no-capture가 설정돼 있어 자동 캡처를 건너뜁니다 — CSV 캡처 코드를 먼저 돌리거나 --no-capture를 빼세요.')
        symbols_to_capture = list(TARGETS.keys()) if args.capture_both else [symbol]
        if args.recapture:
            reason = _ρ('7J6s7Lqh7LKYIOyalOyyreuQqCgtLXJlY2FwdHVyZSk=')
        elif not os.path.exists(args.futures_csv):
            reason = _ρ('Q1NWIOyXhuydjA==')
        else:
            reason = f'CSV에 {symbol} 데이터가 아직 없음'
        print(f'[0/3] 자동 캡처 시작 ({reason}): {symbols_to_capture} — 시간이 좀 걸릴 수 있습니다...')
        run_capture_sync(symbols_to_capture, args.futures_csv)
        print()
    print(f'[1/3] CSV에서 {symbol} 로딩 중... (yfdb는 CME 선물옵션을 지원하지 않아 사전 캡처된 CSV를 씁니다)')
    chain, spot, multiplier = load_futures_symbol(args.futures_csv, symbol)
    print(f'      spot: {spot:.2f} | 계약승수: {multiplier} | 옵션 {len(chain)}행 | 만기: {sorted(chain['expiration'].unique())}')
    n_iv_calls = int(((chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')) & chain[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].notna() & (chain[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')] > 0)).sum())
    n_iv_puts = int(((chain[_ρ('dHlwZQ==')] == _ρ('cHV0')) & chain[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')].notna() & (chain[_ρ('aW1wbGllZFZvbGF0aWxpdHk=')] > 0)).sum())
    n_gamma = int(chain[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].notna().sum())
    print(f'      실제 IV 있는 행: 콜 {n_iv_calls} / 풋 {n_iv_puts}  |  bcdb gamma 있는 행: {n_gamma}행')
    chain = derive_effective_iv_futures(chain, spot, r=0.04)
    n_eff_calls = int(((chain[_ρ('dHlwZQ==')] == _ρ('Y2FsbA==')) & chain[_ρ('aXZfZWZmZWN0aXZl')].notna()).sum())
    n_eff_puts = int(((chain[_ρ('dHlwZQ==')] == _ρ('cHV0')) & chain[_ρ('aXZfZWZmZWN0aXZl')].notna()).sum())
    n_uniq_root = int((chain[_ρ('aXZfc291cmNl')] == _ρ('ZGVsdGFfdW5pcXVl')).sum())
    n_smile = int((chain[_ρ('aXZfc291cmNl')] == _ρ('ZGVsdGFfc21pbGU=')).sum())
    n_from_delta = n_uniq_root + n_smile
    print(f'      delta 역산으로 IV 추가 확보: {n_from_delta}행 (유일근 {n_uniq_root} / 근 2개라 스마일로 선택 {n_smile})  ->  유효 IV(실제+역산): 콜 {n_eff_calls} / 풋 {n_eff_puts}')
    use_bs_mode = n_eff_calls >= args.futures_min_iv_rows and n_eff_puts >= args.futures_min_iv_rows
    print(_ρ('Cj09PT09IOqysOqzvCA9PT09PQ=='))
    print(f'티커: {args.ticker} (내부 심볼: {symbol})')
    print(f'현재가: {spot:.2f}')
    if use_bs_mode:
        print(_ρ('WzIvM10g66qo65OcIEEgKEJsYWNrLTc2IOyKpOy6lCk6IOqwgOyDgSBzcG90IOqwgOqyqeuMgOuzhCBHRVgg6rOE7IKwIOykkS4uLg=='))
        if n_from_delta > 0:
            print(f'      (참고: {n_from_delta}행은 bcdb의 실제 IV가 아니라 delta_bcdb를 Black-76으로 역산한 근사 IV를 사용합니다)')
        price_grid, gex_values = compute_gex_curve_futures_bs(chain, spot, multiplier, 0.04, args.range_pct)
        crossings = find_flip_point(price_grid, gex_values)
        current_gex = np.interp(spot, price_grid, gex_values)
        regime = _ρ('7Y+s7KeA7Yuw67iMIOqwkOuniA==') if current_gex > 0 else _ρ('64Sk6rGw7Yuw67iMIOqwkOuniA==')
        print(f'현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치)')
        print(f'현재 레짐 추정: {regime}')
        if crossings:
            nearest = min(crossings, key=lambda x: abs(x - spot))
            print(f'감마 플립 레벨: {nearest:.2f}  (교차점 {len(crossings)}개, spot={spot:.2f} 대비 {nearest - spot:+.1f}pt / {(nearest - spot) / spot * 100:+.2f}%)')
        else:
            print(_ρ('7Iqk7LqUIOuylOychCDrgrQg6rWQ7LCo7KCQIOyXhuydjCDigJQgLS1yYW5nZS1wY3Trpbwg64qY66Ck67O07IS47JqULg=='))
    elif n_gamma > 0:
        print(_ρ('WzIvM10g66qo65OcIEIgKGJjZGIg7J6Q7LK0IGdhbW1hIOyCrOyaqSk6IElW6rCAIOu2gOyhse2VtCBCUyDsiqTsupTsnYAg7IOd65617ZWY6rOgLCBiY2Ri6rCAIOqzhOyCsO2VtCDrgrTroKTspIAgZ2FtbWHroZwg7ZiE7J6sIOyLnOygkCBHRVjrp4wg6rOE7IKw7ZWp64uI64ukLg=='))
        current_gex, n_c, n_p = compute_current_gex_from_barchart_gamma(chain, spot, multiplier)
        regime = _ρ('7Y+s7KeA7Yuw67iMIOqwkOuniA==') if current_gex > 0 else _ρ('64Sk6rGw7Yuw67iMIOqwkOuniA==')
        print(f'현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치, 콜 {n_c}행/풋 {n_p}행 사용)')
        print(f'현재 레짐 추정: {regime}')
        print(_ρ('6rCQ66eIIO2UjOumvSAn6rCA6rKpIOugiOuyqCfsnYAg6rOE7IKwIOu2iOqwgCDigJQgSVbrj4QgZGVsdGEg7Jet7IKw64+EIOyLpO2MqO2VtOyEnCDqsIDsg4Egc3BvdOycvOuhnCDsnqzqs4TsgrDtlaAg7IiYIOyXhuyKteuLiOuLpC4g7ZiE7J6sIHNwb3TsnbQg7Ja064qQIOyqveyXkCDsnojripTsp4Ao66CI7KeQKeunjCDssLjqs6DtlZjshLjsmpQu'))
        gvals = chain[_ρ('Z2FtbWFfYmFyY2hhcnQ=')].dropna()
        n_zero = int((gvals == 0).sum())
        n_uniq = gvals.nunique()
        if n_uniq <= 39457 ^ _κ or n_zero > 0:
            zero_oi = float(chain.loc[chain[_ρ('Z2FtbWFfYmFyY2hhcnQ=')] == 0, _ρ('b3BlbkludGVyZXN0')].sum())
            total_oi = float(chain[_ρ('b3BlbkludGVyZXN0')].sum())
            print(f'  [경고] bcdb gamma는 소수 4자리 반올림 값이라 고유값이 {n_uniq}종류뿐이고, {n_zero}행은 gamma=0으로 내려와 GEX 기여가 통째로 누락됩니다 (누락 OI {zero_oi:,.0f} / 전체 {total_oi:,.0f} = {zero_oi / max(total_oi, 1):.0%}). 이 모드의 GEX 절대값은 오차가 크니 레짐 방향 정도로만 보세요.')
    else:
        print(_ρ('WzIvM10gSVbrj4QsIGJjZGIgZ2FtbWHrj4Qg65GYIOuLpCDsl4bslrQgR0VYL+ugiOynkC/tlIzrpr0g6rOE7IKw7J20IOu2iOqwgOuKpe2VqeuLiOuLpC4gQ1NWIOy6oeyymCDsvZTrk5zrpbwg64uk7IucIOyLpO2Wie2VtOyEnCBDU1brpbwg7IOI66GcIOuwm+yVhOuztOyEuOyalC4='))
    print(_ρ('ClszLzNdIOy9nOyblC/tkovsm5Qg7YOQ7IOJIOykkSAo64uo7J28IOy1nOuMk+qwkiDrsKnsi50gKyDsiqTrrLTrlKkg67Cp7IudIOuRmCDri6Qg6rOE7IKwKS4uLg=='))
    walls = find_walls_futures_raw(chain)
    walls_sm = find_walls_futures_smoothed(chain, spot, args.futures_wall_bandwidth_pct)
    print(_ρ('W+uLqOydvCDstZzrjJPqsJIg67Cp7IudXQ=='))
    if _ρ('Y2FsbF93YWxsX3N0cmlrZQ==') in walls:
        d = walls[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] - spot
        print(f'  콜월: {walls['call_wall_strike']:.2f}  (콜 OI {walls['call_wall_oi']:,}, spot 대비 {d:+.0f}pt / {d / spot * 100:+.2f}%)')
    if _ρ('cHV0X3dhbGxfc3RyaWtl') in walls:
        d = walls[_ρ('cHV0X3dhbGxfc3RyaWtl')] - spot
        print(f'  풋월: {walls['put_wall_strike']:.2f}  (풋 OI {walls['put_wall_oi']:,}, spot 대비 {d:+.0f}pt / {d / spot * 100:+.2f}%)')
    print(f'[스무딩 방식] (커널 폭={args.futures_wall_bandwidth_pct * 100:.1f}% of spot)')
    if _ρ('Y2FsbF93YWxsX3N0cmlrZQ==') in walls_sm:
        d = walls_sm[_ρ('Y2FsbF93YWxsX3N0cmlrZQ==')] - spot
        print(f'  콜월: {walls_sm['call_wall_strike']:.2f}  (근방 OI 합 {walls_sm['call_wall_region_oi']:,.0f}, spot 대비 {d:+.0f}pt / {d / spot * 100:+.2f}%)')
    if _ρ('cHV0X3dhbGxfc3RyaWtl') in walls_sm:
        d = walls_sm[_ρ('cHV0X3dhbGxfc3RyaWtl')] - spot
        print(f'  풋월: {walls_sm['put_wall_strike']:.2f}  (근방 OI 합 {walls_sm['put_wall_region_oi']:,.0f}, spot 대비 {d:+.0f}pt / {d / spot * 100:+.2f}%)')
    print(_ρ('CuyjvOydmDog7ZGc7KSAIOq3vOyCrCDqsIDsoJUo65Sc65+sIOy9nOyIjy/tkovrobEpIOq4sOuwmOydtOupsCwgc3BvdC/rp4zquLDripQg7Lqh7LKYIOyLnOygkCDqsJLsnoXri4jri6Qu'))
    print(_ρ('7Iuk7Iuc6rCE7J20IOyVhOuLiOudvCDsiqTrg4Xsg7fsnbTrr4DroZwsIOy1nOyLoCDqsJLsnbQg7ZWE7JqU7ZWY66m0IENTViDsuqHsspgg7L2U65Oc66W8IOuLpOyLnCDrj4zroKQgQ1NW66W8IOqwseyLoO2VmOyEuOyalC4='))

def main():
    parser = argparse.ArgumentParser(description=_ρ('6rCQ66eIIO2UjOumvShaZXJvIEdhbW1hKSDroIjrsqgg6rOE7IKw6riw'))
    parser.add_argument(_ρ('LS10aWNrZXI='), default=_ρ('U1BZ'), help=_ρ('7Ji17IWYIOycoOuPmeyEseydtCDsnojripQg7Yuw7LukICjquLDrs7g6IFNQWSkuIE5RL05RPUYvRVMvRVM9RuulvCDso7zrqbQgYmNkYiBDU1Yg6riw67CYIOyEoOusvOyYteyFmCDqsr3roZzroZwg7J6Q64+ZIOyghO2ZmOuQqeuLiOuLpC4='))
    parser.add_argument(_ρ('LS1tYXgtZGF5cw=='), type=int, default=39433 ^ _κ, help=_ρ('7Y+s7ZWo7ZWgIOy1nOuMgCDrp4zquLDsnbzsiJggKOq4sOuzuDogNDXsnbwsIEVURiDqsr3roZzsl5DshJzrp4wg7IKs7JqpKQ=='))
    parser.add_argument(_ρ('LS1yYW5nZS1wY3Q='), type=float, default=0.15, help=_ρ('7ZiE7J6s6rCAIOuMgOu5hCDsiqTsupQg67KU7JyEICjquLDrs7g6IMKxMTUlJSk='))
    parser.add_argument(_ρ('LS1mdXR1cmVzLWNzdg=='), default=FUTURES_CSV_DEFAULT, help=_ρ('Q1NWIOy6oeyymCDsvZTrk5wg6rKw6rO8IENTViDqsr3roZwgKE5RPUYvRVM9RiDsoITsmqksIOq4sOuzuDogYmFyY2hhcnRfb3B0aW9uc19jYXB0dXJlLmNzdik='))
    parser.add_argument(_ρ('LS1mdXR1cmVzLW1pbi1pdi1yb3dz'), type=int, default=FUTURES_MIN_IV_ROWS_DEFAULT, help=_ρ('7L2cL+2SiyDqsIHqsIEg7J20IOqwnOyImCDsnbTsg4Eg7Jyg7ZqoIElW6rCAIOyeiOyWtOyVvCBCUyDsiqTsupQg66qo65OcIOyCrOyaqSAoTlE9Ri9FUz1GIOyghOyaqSwg6riw67O4IDUp'))
    parser.add_argument(_ρ('LS1mdXR1cmVzLXdhbGwtYmFuZHdpZHRoLXBjdA=='), type=float, default=FUTURES_WALL_BANDWIDTH_PCT_DEFAULT, help=_ρ('7Iqk66y065SpIOy9nOyblC/tkovsm5Tsmqkg6rCA7Jqw7Iuc7JWIIOy7pOuEkCDtj60sIHNwb3Qg64yA67mEIOu5hOycqCAoTlE9Ri9FUz1GIOyghOyaqSwg6riw67O4IDAuMDEp'))
    parser.add_argument(_ρ('LS1yZWNhcHR1cmU='), action=_ρ('c3RvcmVfdHJ1ZQ=='), help=_ρ('Q1NW6rCAIOydtOuvuCDsnojslrTrj4QgYmNkYuyXkOyEnCDqsJXsoJzroZwg7IOI66GcIOy6oeyymCAoTlE9Ri9FUz1GIOyghOyaqSk='))
    parser.add_argument(_ρ('LS1jYXB0dXJlLWJvdGg='), action=_ρ('c3RvcmVfdHJ1ZQ=='), help=_ρ('7Lqh7LKY6rCAIO2VhOyalO2VoCDrlYwg7JqU7LKt7ZWcIOyLrOuzvOunjOydtCDslYTri4jrnbwgTlEvRVMg65GYIOuLpCDtlZwg67KI7JeQIOy6oeyymCAoTlE9Ri9FUz1GIOyghOyaqSk='))
    parser.add_argument(_ρ('LS1uby1jYXB0dXJl'), action=_ρ('c3RvcmVfdHJ1ZQ=='), help=_ρ('Q1NW6rCAIOyXhuyWtOuPhCDsnpDrj5kg7Lqh7LKY66W8IOyLnOuPhO2VmOyngCDslYrqs6Ag67CU66GcIOyXkOufrCAoTlE9Ri9FUz1GIOyghOyaqSk='))
    parser.add_argument(_ρ('LS1kZWJ1Zw=='), action=_ρ('c3RvcmVfdHJ1ZQ=='), help=_ρ('W+uUlOuyhOq3uF0g7YOc6re4IOu2meydgCDsg4HshLgg7Lqh7LKYL+2MjOyLsSDroZzqt7jrpbwg7Lac66ClICjquLDrs7jsnYAg6rq87KeQKQ=='))
    args, _unknown = parser.parse_known_args()
    if args.debug:
        global DEBUG_VERBOSE
        DEBUG_VERBOSE = True
    if args.ticker.strip().upper() in FUTURES_TICKER_ALIASES:
        run_futures_mode(args)
        return
    print(f'[1/4] {args.ticker} 옵션체인 로딩 중 (만기 {args.max_days}일 이내)...')
    chain, spot = fetch_chain(args.ticker, args.max_days)
    n_exp = chain[_ρ('ZXhwaXJhdGlvbg==')].nunique()
    print(f'      현재가: {spot:.2f} | 만기 {n_exp}개 | 옵션 {len(chain)}건 로드 완료')
    print(_ρ('WzIvNF0g6rCA7IOBIHNwb3Qg6rCA6rKp64yA67OEIOuEtyDqsJDrp4gg7J217Iqk7Y+s7KCAKEdFWCkg6rOE7IKwIOykkS4uLg=='))
    price_grid, gex_values = compute_gex_curve(chain, spot, price_range_pct=args.range_pct)
    print(_ρ('WzMvNF0g6rCQ66eIIO2UjOumvSDsp4DsoJAg7YOQ7IOJIOykkS4uLg=='))
    crossings = find_flip_point(price_grid, gex_values)
    print(_ρ('WzQvNF0g7L2c7JuUIC8g7ZKL7JuUKE9JIOy1nOuMk+qwkiDtlonsgqzqsIApIO2DkOyDiSDspJEuLi4='))
    walls_by_exp = find_walls(chain)
    walls_agg = find_walls_aggregate(chain)
    current_gex = np.interp(spot, price_grid, gex_values)
    regime = _ρ('7Y+s7KeA7Yuw67iMIOqwkOuniA==') if current_gex > 0 else _ρ('64Sk6rGw7Yuw67iMIOqwkOuniA==')
    print(_ρ('Cj09PT09IOqysOqzvCA9PT09PQ=='))
    print(f'티커: {args.ticker}')
    print(f'현재가: {spot:.2f}')
    print(f'현재가 기준 순 GEX: {current_gex:,.0f} (달러, 1% 변동당 근사치)')
    print(f'현재 레짐 추정: {regime}')
    if crossings:
        nearest = min(crossings, key=lambda x: abs(x - spot))
        print(f'감마 플립(Zero Gamma) 레벨: {nearest:.2f}  (스캔 범위 내 교차점 {len(crossings)}개: {[round(c, 2) for c in crossings]})')
        if spot > nearest:
            print(f'-> 현재가({spot:.2f})가 플립 레벨({nearest:.2f}) 위에 있음: 포지티브 감마 구간')
        else:
            print(f'-> 현재가({spot:.2f})가 플립 레벨({nearest:.2f}) 아래에 있음: 네거티브 감마 구간')
    else:
        print(f'스캔 범위(±{args.range_pct * 100:.0f}%) 내에서 부호 교차가 없습니다. --range-pct 값을 늘려보세요.')
    print(_ρ('Cj09PT09IOy9nOyblCAvIO2Si+yblCA9PT09PQ=='))
    if walls_agg:
        cw = walls_agg.get(_ρ('Y2FsbF93YWxsX3N0cmlrZQ=='))
        cw_oi = walls_agg.get(_ρ('Y2FsbF93YWxsX29p'))
        pw = walls_agg.get(_ρ('cHV0X3dhbGxfc3RyaWtl'))
        pw_oi = walls_agg.get(_ρ('cHV0X3dhbGxfb2k='))
        print(f'[{args.ticker}, 만기 {args.max_days}일 이내 전체 합산 기준]')
        if cw is not None:
            print(f'  콜월: {cw:.2f}  (콜 OI {cw_oi:,})')
        if pw is not None:
            print(f'  풋월: {pw:.2f}  (풋 OI {pw_oi:,})')
    print(f'\n[만기별 상세 — 상위 {min(5, len(walls_by_exp))}개 만기]')
    print(walls_by_exp.head(39457 ^ _κ).to_string(index=False))
    print(_ρ('CuyjvOydmDog7J20IOqzhOyCsOydgCAn65Sc65+s6rCAIOy9nOydgCDsiI8sIO2Si+ydgCDrobEn7J20652864qUIO2RnOykgCDqt7zsgqwg6rCA7KCV7J2EIOyCrOyaqe2VqeuLiOuLpC4='))
    print(_ρ('7Iuk7KCcIOuUnOufrCDtj6zsp4DshZTri53qs7zripQg7LCo7J206rCAIOyeiOydhCDsiJgg7J6I7Jy866mwLCDssLjqs6Dsmqkg7LaU7KCV7LmY7J6F64uI64ukLg=='))
    print(_ρ('7L2c7JuUL+2Si+yblOydgCDsiJzsiJgg7Jik7ZSI7J247YSw66CI7Iqk7Yq4IOq4sOykgOyeheuLiOuLpCDigJQg64us65+sIOqwkOuniCDqsIDspJEg67Cp7Iud6rO864qUIOuLpOuluCDtlonsgqzqsIDqsIAg64KY7JisIOyImCDsnojsirXri4jri6Qu'))
if __name__ == _ρ('X19tYWluX18='):
    main()
