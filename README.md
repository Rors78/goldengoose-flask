# Golden Goose APEX — Flask Edition

Web-based dashboard for monitoring Binance US trading with Golden Goose bot integration.

## Features

- **Web Dashboard**: Browser-based UI at http://127.0.0.1:5000
- **Real-Time Wallet Monitoring**: Live balance tracking
- **Bot Dashboard**: Trading activity monitoring
- **Auto-Refresh**: Client-side JavaScript updates
- **Read-Only Mode**: Safe API key usage
- **Server Time Sync**: Prevents -1021 API errors

## Components

- `app_flask.py` - Main Flask application
- `binance_wallet.py` - Wallet data fetching
- `bot_dashboard.py` - Bot monitoring interface
- `templates/` - HTML templates
- `static/` - CSS/JS assets

## Installation

```bash
pip install -r requirements_flask.txt
```

## Configuration

### Option 1: Environment Variables (Recommended)
```bash
export BINANCE_API_KEY='your_key_here'
export BINANCE_SECRET_KEY='your_secret_here'
```

### Option 2: JSON File
Create `binance_us.json`:
```json
{
  "apiKey": "your_key_here",
  "secret": "your_secret_here"
}
```

**Important**: Use **read-only** API keys for security!

## Usage

### Windows
```batch
run_flask.bat
```

### Linux/Mac
```bash
python app_flask.py
```

Then open http://127.0.0.1:5000 in your browser.

## Features

### Wallet View
- Current balances
- USD equivalent values
- Total portfolio value

### Bot Dashboard
- Active positions
- Recent trades
- Performance metrics

### Auto-Refresh
- Configurable refresh interval
- Client-side updates (no page reload)
- Modify interval in template

## Troubleshooting

### -1021 Time Sync Errors
- Keep "Use server time sync" enabled (default)
- Ensure system clock is accurate

### Connection Issues
- Verify API keys are correct
- Check Binance US endpoint accessibility
- Ensure read-only permissions

### Port Already in Use
Edit `app_flask.py`:
```python
app.run(port=5001)  # Change port
```

## Security

- Uses read-only API keys
- No order execution capabilities
- Local-only server (127.0.0.1)
- Keys not stored in code

## Customization

### Change Refresh Rate
Edit template HTML:
```javascript
setInterval(refreshData, 10000); // 10 seconds
```

### Add Custom Metrics
Extend `bot_dashboard.py` with additional calculations.

## License

Provided as-is for personal use.

---

**Monitor your Golden Goose in style** 🦢✨
