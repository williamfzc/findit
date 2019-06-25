FROM python:3-slim

USER root

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN apt-get update \
    # opencv
    && apt-get install -y libglib2.0 libsm6 libxrender1 libxext-dev \
    # ocr
    && apt-get -y install tesseract-ocr tesseract-ocr-chi-sim libtesseract-dev libleptonica-dev pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt

COPY . .

RUN pip install --no-cache-dir . \
    && pip install tesserocr

EXPOSE 9410

CMD ["python", "-m", "findit.server", "--dir", "/root/pics"]
