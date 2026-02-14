# Amazon Marketing Automation
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set working directory to src
WORKDIR /app/src

# Run the automation
CMD ["python", "main.py"]