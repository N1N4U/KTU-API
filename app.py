# app.py
from flask import Flask, request, jsonify, Response
import json
from dotenv import load_dotenv
load_dotenv()
import os
import logging
import socket
from pythonjsonlogger import jsonlogger
import coloredlogs
from scraper import scrape_ktu_data


def configure_logging():
    """Configure structured JSON logging to stdout using environment LOG_LEVEL with color support."""
    # respect LOG_LEVEL env var, default to INFO
    level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Configure coloredlogs for console output
    coloredlogs.install(
        level=level,
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        field_styles={
            'asctime': {'color': 'cyan'},
            'levelname': {'color': 'green', 'bold': True},
            'name': {'color': 'blue'}
        },
        level_styles={
            'debug': {'color': 'white'},
            'info': {'color': 'green'},
            'warning': {'color': 'yellow', 'bold': True},
            'error': {'color': 'red', 'bold': True},
            'critical': {'color': 'red', 'bold': True, 'background': 'white'}
        }
    )


configure_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)


def _get_local_ip():
    """Return the primary LAN IP address for this host (or None)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This does not send any data. It simply lets the OS pick a source IP.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass
    # fallback: try hostname resolution
    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        if host_ip and not host_ip.startswith("127."):
            return host_ip
    except Exception:
        pass
    return None

# Serve the website frontend
@app.route('/')
def index():
    """Serve the KTU API tester website."""
    from flask import send_from_directory
    return send_from_directory('website', 'index.html')

@app.route('/website/<path:filename>')
def website_static(filename):
    """Serve static website assets."""
    from flask import send_from_directory
    return send_from_directory('website', filename)

# CHANGED: The API endpoint is now /api/student
@app.route('/api/student', methods=['POST'])
def handle_api_request():
    logger.info("API endpoint /api/student was hit")

    json_data = request.get_json()

    if not json_data:
        return jsonify({"status": "error", "error_message": "No JSON data provided in request."}), 400

    username = json_data.get('username')
    password = json_data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "error_message": "Missing 'username' or 'password' in request body."}), 400
    
    logger.info("Received request for username", extra={"username": username})

    scraped_data = scrape_ktu_data(username, password)
    
    logger.info("Scraping complete. Sending response back to the user.")

    # This check now correctly handles the login error from the scraper
    if scraped_data.get("status") == "error":
        # For login failures, return 401 Unauthorized
        logger.error("Scraper returned error", extra={"error": scraped_data.get("error_message")})
        if "Login failed" in scraped_data.get("error_message", ""):
            return jsonify(scraped_data), 401
        # For other server-side issues
        else:
            return jsonify(scraped_data), 500
            
    # If successful, create a pretty-printed JSON response
    pretty_json = json.dumps(scraped_data, indent=4)
    response = Response(pretty_json, mimetype='application/json', status=200)
    logger.info("Responding with scraped data", extra={"username": username})

    return response

if __name__ == '__main__':
    # Read SERVER_PORT from environment (populated by .env via load_dotenv())
    port_str = os.environ.get('SERVER_PORT')
    if port_str is None:
        logger.warning("`SERVER_PORT` not set in environment; using default 5000")
        port = 5000
    else:
        try:
            port = int(port_str)
        except ValueError:
            logger.warning("Invalid SERVER_PORT '%s'; using default 5000", port_str)
            port = 5000

    # Compute useful access URLs to show in the console
    urls = [f"http://127.0.0.1:{port}"]
    local_ip = _get_local_ip()
    if local_ip and local_ip != '127.0.0.1':
        urls.append(f"http://{local_ip}:{port}")

    # log the accessible URLs in a human-friendly single line
    logger.info("Starting Flask app — available at: %s", " | ".join(urls))

    # Run the Flask development server bound to all interfaces so LAN IP works
    app.run(host='0.0.0.0', port=port)