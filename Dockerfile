FROM python:3.7
ENV PYTHONBUFFERED 1
RUN mkdir /config
ADD requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /app
RUN locale-gen ru_RU
RUN locale-gen ru_RU.UTF-8
RUN update-locale
ADD . /app
WORKDIR /app
ENTRYPOINT ["/bin/bash", "start.sh"]
