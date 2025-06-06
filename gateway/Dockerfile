FROM python:3.9-slim

WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir -r requirements.txt
# 애플리케이션 코드 복사
COPY . .

# 포트 8080 지정 (고정)
EXPOSE 8080

# API 게이트웨이 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]