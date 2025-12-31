# Golden Goose APEX — Flask Edition

Runs locally without Streamlit. Browser-based UI at http://127.0.0.1:5000

## Setup
1) Put your Binance US **read-only** API keys into environment variables:
   - `BINANCE_API_KEY`
   - `BINANCE_SECRET_KEY`
   (Optionally provide a `binance_us.json` with `{"apiKey":"...", "secret":"..."}` in the same folder.)

2) Double‑click `run_flask.bat` (Windows). It will install dependencies and launch the app.
   - Or run manually:
     ```bash
     pip install -r requirements_flask.txt
     python app_flask.py
     ```

## Notes
- Auto-refresh is client-side JS; you can change the interval at the top of the page.
- Endpoint defaults to `https://api.binance.us`.
- If you see `-1021` errors, keep "Use server time sync" enabled (it is by default).
