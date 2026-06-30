# ╔══════════════════════════════════════════════════════════════╗
# ║           Dockerfile — XivaSudev Music Bot                  ║
# ║   For VPS / self-hosting. Render uses render.yaml instead.  ║
# ╚══════════════════════════════════════════════════════════════╝

FROM python:3.11-slim-bullseye

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies first (layer caching) ─────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy source code ───────────────────────────────────────────────────────────
COPY . .

# ── Create runtime directories ─────────────────────────────────────────────────
RUN mkdir -p logs downloads

# ── Expose keep-alive port ────────────────────────────────────────────────────
EXPOSE 8080

# ── Start bot ─────────────────────────────────────────────────────────────────
CMD ["python3", "main.py"]
