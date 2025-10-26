FROM rayproject/ray:2.9.1-py310

WORKDIR /app

# Install worker dependencies (needed for remote actors to execute on head node)
RUN pip install --no-cache-dir \
    docker==7.0.0 \
    pika==1.3.2 \
    python-dotenv==1.0.0 \
    httpx==0.26.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0

# Add ray user to docker group for Docker socket access
USER root
RUN groupadd -g 999 docker || true && \
    usermod -aG docker ray
USER ray
