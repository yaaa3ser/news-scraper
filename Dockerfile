FROM python:3.9
WORKDIR /app

# Install dependencies for Chrome and chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    fonts-liberation \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Use Chrome for Testing (guaranteed compatibility)
RUN CHROME_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | jq -r '.channels.Stable.version') \
    && echo "Installing Chrome version: $CHROME_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chrome-linux64.zip" \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -s /opt/chrome/chrome /usr/local/bin/google-chrome \
    && rm chrome-linux64.zip

# Install matching ChromeDriver
RUN CHROME_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | jq -r '.channels.Stable.version') \
    && echo "Installing ChromeDriver version: $CHROME_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Verify installations
RUN google-chrome --version
RUN chromedriver --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]