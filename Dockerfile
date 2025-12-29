FROM python:3.9-slim

# Install system dependencies including Google Chrome
# Install wget, gnupg, and other dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends

# Add Google Chrome's official GPG key and repository
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install Google Chrome Stable
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY sheinverse.py .

# Set environment variable to enable headless mode in our script
ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python", "sheinverse.py"]
