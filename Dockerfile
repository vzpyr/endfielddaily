FROM python:3.14-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir python-dotenv schedule curl_cffi
RUN useradd -u 1000 -s /usr/sbin/nologin endfielddaily
COPY endfielddaily.py .
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
USER endfielddaily
ENTRYPOINT ["python", "-u", "/app/endfielddaily.py"]