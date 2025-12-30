FROM python:3.9-slim-bullseye

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PORT 5000
ENV USERNAME admin
ENV PASSWORD admin
ENV OPENSSL_CONF /etc/ssl/

COPY . /app

WORKDIR /app

RUN set -x; buildDeps='wget build-essential' \
&& apt-get update && apt-get install -y ${buildDeps} \ 
chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev \
chromium chromium-driver fonts-wqy-zenhei \
&& rm -rf /var/lib/apt/lists/* \
&& pip install --upgrade "setuptools<58.0.0" \
&& pip install -r requirements.txt && pip cache purge \
&& apt-get purge -y --auto-remove $buildDeps

EXPOSE $PORT

RUN sed -i 's/\r$//' run.sh && chmod +x run.sh
CMD ./run.sh $PORT $USERNAME $PASSWORD
