FROM python:3-slim

USER root

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN apt-get update \
    # opencv
    && apt-get install -y libglib2.0 libsm6 libxrender1 libxext-dev \
    # ocr
    && apt-get -y install gcc build-essential tesseract-ocr tesseract-ocr-chi-sim libtesseract-dev libleptonica-dev pkg-config \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir Pillow \
    && pip install --no-cache-dir tesserocr \
    && pip install --no-cache-dir findtext \
    && pip install --no-cache-dir jieba \
    && apt-get purge -y --auto-remove gcc build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV LC_ALL=C

EXPOSE 9410

CMD ["python", "-m", "findit.server", "--dir", "/root/pics"]
