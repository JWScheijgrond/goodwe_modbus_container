FROM python:3.12.2-alpine3.19 AS base

RUN apk add --update \
    tzdata

FROM python:3.12.2-alpine3.19

WORKDIR /source

COPY --from=base /usr/share/zoneinfo /usr/share/zoneinfo

ENV TZ=Europe/Amsterdam

COPY requirements.txt script.py ./

RUN pip3 install -r requirements.txt --upgrade

USER root

# Enable the logging output
ENV PYTHONUNBUFFERED=1
# Settings to update or pass when running the container
ENV PVO_APIKEY="PVOUTPUTAPIKEY"
ENV PVO_SYSTEMID="1111111"
ENV INV_IP="192.168.0.239"
ENV INV_FAM="D-NS"


CMD ["python", "script.py"]

