FROM rayproject/ray:2.9.1-py310

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system .

# Copy application
COPY . .

# Run worker
CMD ["python", "main.py"]
