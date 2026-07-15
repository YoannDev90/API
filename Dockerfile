FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-generated prisma client (from GitHub Actions)
COPY node_modules/.prisma node_modules/.prisma
COPY node_modules/@prisma/client node_modules/@prisma/client

COPY . .

EXPOSE 10000
CMD ["bash", "start.sh"]
