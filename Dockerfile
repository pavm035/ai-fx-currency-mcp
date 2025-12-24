# Base image for python version
FROM python:3.13-slim

# Work directory in the container
WORKDIR /app

# Copy dependency files first (for better caching)
COPY requirements.txt pyproject.toml ./

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the server code
COPY . .

# Open a port for incoming connections
EXPOSE 8080

# Make Python output visible in logs
ENV PYTHONUNBUFFERED=1

# Run the server (it starts uvicorn internally)
CMD ["python", "fx_mcp_server.py"]