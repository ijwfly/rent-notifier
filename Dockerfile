FROM python:3.7
ENV PYTHONBUFFERED 1
RUN mkdir /config
ADD requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /app
ADD . /app
WORKDIR /app
ENTRYPOINT ["/bin/bash", "start.sh"]
