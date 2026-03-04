"""
API-клиент с полным набором браузерных заголовков для обхода Imunify360.

Ключевая идея: имитация браузера — Session + warmup (GET главной) + cookies.
Imunify360 часто требует "первый заход" на сайт, чтобы выдать cookie.

На residential IP заголовки не помогают — блокировка по IP. Решения:
- WC_HTTPS_PROXY / HTTPS_PROXY — прокси с datacenter egress
- railway run — запросы идут с IP Railway
"""

import os
import re
import random
import time
from typing import Optional
from woocommerce import API

IMUNIFY360_RETRIES = 4
IMUNIFY360_RETRY_DELAYS = (3, 6, 12, 20)  # Усиленные задержки


def _chrome_version_from_ua(user_agent: str) -> str:
    """Извлечь версию Chrome из User-Agent (совпадение важно для Imunify360)."""
    if not isinstance(user_agent, str) or not user_agent:
        return "131"
    m = re.search(r"Chrome/(\d+)", user_agent, re.I)
    return m.group(1) if m else "131"


def _browser_headers(user_agent: str, store_url: str) -> dict:
    """Заголовки как у браузера. sec-ch-ua версия = Chrome из User-Agent."""
    ua = str(user_agent) if user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
    base = store_url.rstrip("/") + "/"
    v = _chrome_version_from_ua(ua)
    return {
        "user-agent": ua,
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "referer": base,
        "sec-ch-ua": f'"Not:A-Brand";v="99", "Google Chrome";v="{v}", "Chromium";v="{v}"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


def _resolve_proxies(proxy_url: Optional[str] = None) -> Optional[dict]:
    """Сформировать proxies для requests (http/https)."""
    url = proxy_url or os.getenv("WC_HTTPS_PROXY") or os.getenv("HTTPS_PROXY")
    if not url or not str(url).strip():
        return None
    return {"http": url, "https": url}


def _warmup_session(
    session, store_url: str, headers: dict, verify_ssl: bool, timeout: int,
    proxies: Optional[dict] = None
) -> None:
    """GET главной и wp-json — Imunify360 может выдать cookie при первом визите."""
    base = store_url.rstrip("/") + "/"
    urls = [base, base + "wp-json/"]
    for url in urls:
        for attempt in range(3):
            try:
                r = session.get(
                    url, headers=headers, verify=verify_ssl, timeout=timeout, proxies=proxies
                )
                if r.status_code == 200 and "imunify360" not in (r.text or "").lower():
                    break
            except Exception:
                pass
            time.sleep(2 + random.uniform(0, 1))


def patch_api_with_browser_headers(
    api: API, store_url: str, proxy_url: Optional[str] = None
) -> None:
    """
    Патчит WooCommerce API: Session + warmup (GET главной) + браузерные заголовки.
    Imunify360 часто блокирует API без предварительного визита на сайт (cookie).
    proxy_url: URL прокси (WC_HTTPS_PROXY / HTTPS_PROXY) для обхода с residential IP.
    """
    from requests import Session

    _headers = _browser_headers(api.user_agent, store_url)
    _proxies = _resolve_proxies(proxy_url)
    _session = Session()
    _session.headers.update(_headers)
    _session.trust_env = True  # подхватывает HTTP_PROXY/HTTPS_PROXY из env
    _warmup_done = [False]  # mutable для замыкания

    def _patched_request(method, endpoint, data, params=None, **kwargs):
        if params is None:
            params = {}
        url = api._API__get_url(endpoint)
        auth = None
        headers = dict(_headers)
        request_params = params

        if api.is_ssl and not api.query_string_auth:
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(api.consumer_key, api.consumer_secret)
        elif api.is_ssl and api.query_string_auth:
            request_params = dict(params)
            request_params.update({
                "consumer_key": api.consumer_key,
                "consumer_secret": api.consumer_secret
            })
        else:
            from urllib.parse import urlencode
            from time import time as _oauth_time
            from woocommerce.oauth import OAuth
            encoded_params = urlencode(params)
            url = f"{url}?{encoded_params}"
            url = OAuth(
                url=url,
                consumer_key=api.consumer_key,
                consumer_secret=api.consumer_secret,
                version=api.version,
                method=method,
                oauth_timestamp=kwargs.get("oauth_timestamp", int(_oauth_time()))
            ).get_oauth_url()
            request_params = {}  # params уже в url (OAuth)

        if data is not None:
            import json
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            headers["content-type"] = "application/json;charset=utf-8"

        if not _warmup_done[0]:
            _warmup_done[0] = True
            time.sleep(random.uniform(0.5, 1.5))  # jitter перед warmup
            _warmup_session(
                _session, store_url, headers, api.verify_ssl, api.timeout, _proxies
            )

        request_kw = {"proxies": _proxies} if _proxies else {}
        for attempt in range(IMUNIFY360_RETRIES):
            resp = _session.request(
                method=method,
                url=url,
                verify=api.verify_ssl,
                auth=auth,
                params=request_params,
                data=data,
                timeout=api.timeout,
                headers=headers,
                **request_kw,
                **{k: v for k, v in kwargs.items() if k not in ("oauth_timestamp",)}
            )
            if resp.status_code != 200:
                return resp
            text = (resp.text or "").lower()
            if "imunify360" not in text and "bot-protection" not in text:
                return resp
            if attempt < IMUNIFY360_RETRIES - 1:
                delay = IMUNIFY360_RETRY_DELAYS[min(attempt, len(IMUNIFY360_RETRY_DELAYS) - 1)]
                time.sleep(delay)
        return resp

    api._API__request = _patched_request
