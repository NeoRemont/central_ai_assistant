#!/bin/bash
uvicorn main:app --host 0.0.0.0 --port 10000
apt-get update && apt-get install -y ffmpeg
