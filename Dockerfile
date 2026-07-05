# Stage 1: builder - installs dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy only the dependency file first - this is a layer-caching trick.
# Docker caches each instruction as a layer; if requirements.txt hasn't
# changed, this pip install layer is reused instead of re-run, even if
# your actual code changed. Same principle as Maven's dependency
# caching in a multi-stage CI build, just expressed as Docker layers
# instead of a .m2 cache.
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: runtime - the actual image that ships
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from the builder stage, not the builder
# stage itself - this is the multi-stage part. The final image never
# sees pip's build tools/cache, only the installed result. Java
# comparison: this is the same idea as a multi-stage build that
# compiles with a full JDK in stage 1, then copies only the built JAR
# into a slim JRE-only image in stage 2 - you ship the output, not the
# toolchain that built it.
COPY --from=builder /root/.local /root/.local
COPY api/ ./api/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Make sure the --user-installed packages are on PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]