FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir cryptography

# 애플리케이션 코드 복사
COPY . .

# Python 모듈 경로 설정
ENV PYTHONPATH=/app

# 서비스 설정
ENV SERVICE_NAME=service1
ENV SERVICE_PORT=8001

# 포트 노출
EXPOSE 8001

# 환경변수 포트로 uvicorn 실행
CMD uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT}