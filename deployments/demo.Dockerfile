FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/src/
COPY demo/ /app/demo/
CMD ["tail", "-f", "/dev/null"]