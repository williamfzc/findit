FROM python:3-slim

USER root

RUN apt-get update \
    && apt-get install -y libglib2.0 libsm6 libxrender1 libxext-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir findit==0.4.3

EXPOSE 9410

WORKDIR /root/pics

CMD ["python", "-m", "findit.server", "--dir", "/root/pics"]
