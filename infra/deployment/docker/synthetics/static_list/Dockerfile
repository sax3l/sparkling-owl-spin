FROM python:3.11-slim

WORKDIR /app

# Installera Flask och grundläggande verktyg
RUN pip install --no-cache-dir flask==3.0.2 && \
    apt-get update && apt-get install -y wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Kopiera applikation
COPY synthetics/static_list/app.py .

EXPOSE 8081

# Hälsokontroll
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8081/ || exit 1

CMD ["python", "app.py"]
