FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY api/ ./api/
COPY src/ ./src/
COPY config.py .

# Create output directories with write permissions for HF Spaces
RUN mkdir -p data outputs/plots \
    && chmod -R 777 data outputs

# HF Spaces runs as non-root user (uid 1000)
RUN useradd -m -u 1000 hfuser
USER hfuser

# HF Spaces uses port 7860
EXPOSE 7860

# Run the app on port 7860
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]
