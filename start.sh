#!/bin/bash
source penv/Scripts/activate
exec gunicorn -k eventlet -w 1 -b :$PORT app:app
