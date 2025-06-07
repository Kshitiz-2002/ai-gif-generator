FROM node:18-slim AS frontend-build
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend .
RUN npm run build

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

COPY --from=frontend-build /app/frontend/dist /app/static

RUN mkdir -p /app/uploads /app/gifs

ENV UPLOAD_FOLDER=/app/uploads
ENV GIF_OUTPUT_DIR=/app/gifs

RUN chmod +x /app/start.sh /app/scripts/*.sh

EXPOSE 5000

CMD ["./start.sh"]
