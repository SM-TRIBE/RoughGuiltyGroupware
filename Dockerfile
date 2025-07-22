# Dockerfile

# 1. Start with a stable Python base image
FROM python:3.11-slim

# 2. Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# 3. Install the Rust compiler inside the image
# This is the key step to solve the compilation error reliably
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
# Add Rust to the PATH environment variable
ENV PATH="/root/.cargo/bin:${PATH}"

# 4. Set a working directory inside the image
WORKDIR /app

# 5. Copy and install dependencies
# This caches the dependency installation layer, speeding up future builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code into the image
COPY . .

# 7. Expose the port Gunicorn will run on
# Render will use this port to communicate with your app.
EXPOSE 10000

# 8. Define the command to run your application
# This is the same start command as before, but run inside the container.
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--worker-class", "uvicorn.workers.UvicornWorker"]
