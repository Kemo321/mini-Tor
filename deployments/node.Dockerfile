FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/src/
RUN mkdir -p /app/certs
CMD ["python3", "-m", "src.node.main"]
