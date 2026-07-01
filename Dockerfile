FROM python:3.14-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir python-dotenv schedule curl_cffi
COPY endfielddaily.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "endfielddaily.py"]
