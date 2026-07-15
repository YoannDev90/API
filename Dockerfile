# Build stage - generate prisma with limited memory
FROM node:20-slim AS builder
WORKDIR /app
RUN npm install prisma @prisma/client
COPY schema.prisma .
ENV NODE_OPTIONS="--max-old-space-size=256"
RUN npx prisma generate

# Runtime stage
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the generated engine binary and client
COPY --from=builder /app/node_modules/.prisma /app/node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma/client /app/node_modules/@prisma/client

COPY . .

EXPOSE 10000
CMD ["bash", "start.sh"]
