FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY mcp_server mcp_server
COPY sample-data sample-data
COPY evals evals

ENV HOST=0.0.0.0
ENV PORT=8060

EXPOSE 8060
CMD ["python", "-m", "backend.app"]

