# Build from the track root, because the service needs genai_kit and course_data:
#   docker build -f "08_Production deployment and MLOps for GenAI/Dockerfile" -t genai-service:1.0.0 .

# ---- Build stage: compilers and caches stay here, out of the final image
FROM python:3.13-slim AS build
WORKDIR /build
COPY ["08_Production deployment and MLOps for GenAI/requirements-service.txt", "requirements.txt"]
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    APP_VERSION=1.0.0
COPY --from=build /install /usr/local

WORKDIR /app
COPY genai_kit ./genai_kit
COPY course_data ./course_data
COPY ["08_Production deployment and MLOps for GenAI/project", "./project"]

# Never run as root inside a container.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/readyz', timeout=2)"

# Secrets arrive as environment variables at runtime. They are never baked into the image.
# One worker per container: metrics and the budget counter live in process memory, so more
# workers would give inconsistent numbers. Scale by running more containers.
CMD ["uvicorn", "project.main:app", "--host", "0.0.0.0", "--port", "8080"]
