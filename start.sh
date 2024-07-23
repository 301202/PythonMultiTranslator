#!/bin/bash
source venv/bin/activate
exec gunicorn -k eventlet -w 1 -b :$PORT app:app