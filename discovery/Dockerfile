FROM python:3.9-slim

WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 8762 지정 (고정)
EXPOSE 8762

# 디스커버리 서비스 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8762"]