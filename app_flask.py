from flask import Flask, render_template, request, jsonify
import os
from binance_wallet import BinanceWallet

def create_app():
    app = Flask(__name__)

    # Defaults
    DEFAULT_REFRESH = 30
    DEFAULT_BASE_URL = "https://api.binance.us"

    def get_wallet(base_url=None, use_server_time=True):
        api_key = os.getenv("BINANCE_API_KEY")
        secret_key = os.getenv("BINANCE_SECRET_KEY")
        return BinanceWallet(api_key=api_key, secret_key=secret_key,
                             base_url=(base_url or DEFAULT_BASE_URL),
                             use_server_time=use_server_time)

    @app.route("/")
    def index():
        refresh = int(request.args.get("refresh", DEFAULT_REFRESH))
        base_url = request.args.get("base_url", DEFAULT_BASE_URL)
        use_server_time = request.args.get("server_time", "1") == "1"
        # Render page; balances are fetched via /api/balances to keep page snappy
        return render_template("index.html",
                               refresh=refresh,
                               base_url=base_url,
                               use_server_time=use_server_time)

    @app.get("/api/balances")
    def api_balances():
        base_url = request.args.get("base_url", DEFAULT_BASE_URL)
        use_server_time = request.args.get("server_time", "1") == "1"
        wallet = get_wallet(base_url=base_url, use_server_time=use_server_time)
        data = wallet.get_balances()
        # Normalize for UI
        if isinstance(data, dict) and "error" in data:
            return jsonify({"ok": False, "error": str(data["error"])}), 200
        return jsonify({"ok": True, "balances": data}), 200

    @app.get("/api/health")
    def api_health():
        return jsonify({"ok": True}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
