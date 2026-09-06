FROM python:3.14-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir python-dotenv schedule curl_cffi && \
    useradd -u 1000 -M endfielddaily
COPY endfielddaily.py ./
USER endfielddaily
ENTRYPOINT ["python", "-u", "/app/endfielddaily.py"]
