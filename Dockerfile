FROM python:3.12-slim

# Install Node.js for prisma
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Generate prisma client from litellm's schema
RUN cp /usr/local/lib/python3.12/site-packages/litellm/proxy/schema.prisma /app/schema.prisma && \
    prisma generate

# Copy app
COPY . .

EXPOSE 10000

CMD ["bash", "start.sh"]
