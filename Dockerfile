FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget unzip curl gnupg \
    && mkdir -p /usr/share/man/man1

RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

RUN CHROMEDRIVER_VERSION=$(curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE") \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "webScrape.scrape_api:app"]
