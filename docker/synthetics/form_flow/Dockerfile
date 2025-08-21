FROM python:3.11-alpine

# Install Python dependencies  
RUN pip install flask==2.3.3 faker==19.6.2

# Create app directory
WORKDIR /app

# Copy application
COPY app.py .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8083/ || exit 1

# Expose port
EXPOSE 8083

# Run application
CMD ["python", "app.py"]
