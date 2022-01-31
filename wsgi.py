#!/usr/bin/python3
"""
    wsgi.py
"""

from argostime import create_app

app = create_app()
if __name__ == "__main__":
    app.run()
