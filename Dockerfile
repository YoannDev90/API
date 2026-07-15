FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy schema and generate prisma client with limited memory
COPY schema.prisma .
RUN NODE_OPTIONS="--max-old-space-size=256" prisma generate

COPY . .

EXPOSE 10000
CMD ["bash", "start.sh"]
