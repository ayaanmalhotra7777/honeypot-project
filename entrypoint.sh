#!/bin/sh
# Entry point script to handle environment variables
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
