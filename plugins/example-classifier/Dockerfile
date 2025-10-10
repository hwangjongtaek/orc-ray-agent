FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system .

COPY main.py .
COPY plugin.json .

ENTRYPOINT ["python", "main.py"]
