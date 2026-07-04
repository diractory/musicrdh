FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git curl wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    -o /usr/local/bin/yt-dlp && chmod a+rx /usr/local/bin/yt-dlp

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p downloads

CMD ["python", "bot.py"]
