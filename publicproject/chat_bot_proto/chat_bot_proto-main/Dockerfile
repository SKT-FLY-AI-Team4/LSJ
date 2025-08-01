# 나비얌 챗봇 Docker 이미지
FROM python:3.11-slim

# 메타데이터
LABEL maintainer="naviyam-team"
LABEL description="나비얌 - 어린이 대상 착한가게 추천 AI 챗봇"
LABEL version="1.0.0"

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p /app/outputs /app/cache /app/data

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 포트 노출
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 비root 사용자 생성 및 권한 설정
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 시작 명령어
CMD ["python", "test_simple_server.py"]