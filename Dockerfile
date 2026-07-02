FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY api/ ./api/
COPY src/ ./src/
COPY config.py .

# Create output directories
RUN mkdir -p data outputs/plots

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
