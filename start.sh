#!/bin/bash

# 레포지토리에서 최신 버전 pull 받기
git pull origin main

# 서버 실행
python3 ./server.py