import os, time, json, hmac, hashlib, requests
from urllib.parse import urlencode

class BinanceWallet:
    def __init__(self, api_key=None, secret_key=None, config_path="binance_us.json",
                 base_url="https://api.binance.us", use_server_time=True):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.secret_key = secret_key or os.getenv("BINANCE_SECRET_KEY")
        if (self.api_key is None or self.secret_key is None) and os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    creds = json.load(f)
                self.api_key = self.api_key or creds.get("apiKey")
                self.secret_key = self.secret_key or creds.get("secret")
            except Exception:
                pass
        self.base_url = base_url.rstrip("/")
        self.use_server_time = use_server_time

    def _server_time(self):
        try:
            r = requests.get(f"{self.base_url}/api/v3/time", timeout=5)
            if r.status_code == 200:
                return r.json().get("serverTime")
        except Exception:
            pass
        return None

    def _timestamp(self):
        if self.use_server_time:
            t = self._server_time()
            if isinstance(t, int):
                return t
        return int(time.time() * 1000)

    def _sign_request(self, params):
        if not self.secret_key:
            raise ValueError("Missing Binance API secret key")
        query = urlencode(params)
        signature = hmac.new(self.secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()
        return f"{query}&signature={signature}"

    def _headers(self):
        if not self.api_key:
            raise ValueError("Missing Binance API key")
        return {"X-MBX-APIKEY": self.api_key}

    def get_balances(self, timeout=10, retries=8, backoff=1.5):
        if not self.api_key or not self.secret_key:
            return {"error": "Missing API credentials. Set BINANCE_API_KEY and BINANCE_SECRET_KEY, or provide binance_us.json."}
        attempt, last_err = 0, None
        while attempt < retries:
            attempt += 1
            try:
                ts = self._timestamp()
                url = f"{self.base_url}/api/v3/account?{self._sign_request({'timestamp': ts})}"
                r = requests.get(url, headers=self._headers(), timeout=timeout)
                data = r.json() if r.headers.get("content-type","").startswith("application/json") else r.text
                if r.status_code == 200 and isinstance(data, dict) and "balances" in data:
                    return {b.get("asset"): float(b.get("free", 0.0))
                            for b in data.get("balances", [])
                            if float(b.get("free", 0.0)) > 0}
                if isinstance(data, dict) and str(data.get("code")) in ("-1021","-1022"):
                    self.use_server_time = True
                last_err = data
            except Exception as e:
                last_err = f"HTTP error: {e}"
            time.sleep(max(0.5, backoff ** attempt))
        return {"error": last_err if last_err else "Unknown error after retries"}
