"""
Entry point for the CDOE Complaint Management System.

Usage (on the office PC):
    python run.py

This starts the Flask development server. For a small, single-PC internal
tool this is sufficient — no WSGI server / reverse proxy is required.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
