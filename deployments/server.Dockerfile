FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/src/
COPY demo/ /app/demo/
COPY scripts/ /app/scripts/
RUN mkdir -p /app/certs
RUN chmod +x /app/scripts/*.sh
RUN ./scripts/setup_certs.sh
CMD ["python3", "demo/target_server.py"]
