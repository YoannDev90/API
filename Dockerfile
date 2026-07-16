FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prisma_client/ /usr/local/lib/python3.12/site-packages/prisma/
COPY litellm_config.yaml .

EXPOSE 10000
CMD ["litellm", "--config", "litellm_config.yaml", "--port", "10000", "--host", "0.0.0.0"]
