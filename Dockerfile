# 1. Start from an official image that already has Python installed.
#    "slim" is a smaller Linux variant, which makes the image faster to build and download.
FROM python:3.12-slim

# 2. Set the working directory INSIDE the container.
#    All following commands run from /app.
WORKDIR /app

# 3. Copy ONLY the requirements file first, then install the packages.
#    Docker caches each step (layer). As long as requirements.txt doesn't change,
#    this slow step is reused, and editing your code doesn't trigger a reinstall.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Now copy your code into the container.
COPY app/ ./app

# 5. Document which port the app listens on (informational; -p does the actual mapping).
EXPOSE 8000

# 6. The command that runs when the container starts.
#    --host 0.0.0.0 is required: it makes the app accept connections from OUTSIDE
#    the container. The default, 127.0.0.1, would only be reachable from inside it.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]