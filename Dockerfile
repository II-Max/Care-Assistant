# ============================================
# 🏥 Dockerfile — AI Customer Care Assistant
# Bệnh viện Tim Hà Nội
# ============================================
#
# Multi-stage build:
#   Stage 1: builder — install dependencies
#   Stage 2: runtime — production image
#
# Build:
#   docker build -t care-assistant:latest .
#
# Run:
#   docker run -p 8001:8001 --env-file .env care-assistant:latest
#
# ============================================

# ========================
# Stage 1: Builder
# ========================
FROM python:3.11-slim AS builder

LABEL maintainer="Bệnh viện Tim Hà Nội - AI Team"
LABEL description="AI Customer Care Assistant — RAG-based chatbot"

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY ai-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# ========================
# Stage 2: Runtime
# ========================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ai-service/ ai-service/
COPY knowledge/ knowledge/
COPY Data/ Data/
COPY frontend/ frontend/
COPY .env.example .env.example

# Create necessary directories
RUN mkdir -p /app/chroma_db

# Non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/api/ai/health || exit 1

# Run with gunicorn + uvicorn workers (production)
CMD ["gunicorn", "ai-service.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8001", \
     "--workers", "2", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--log-level", "info"]
