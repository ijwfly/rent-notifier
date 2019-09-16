FROM python:3.7.4-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
ADD requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /app
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LC_ALL "ru_RU.UTF-8"
ENV LANG "ru_RU.UTF-8"
RUN update-locale
ADD . /app
WORKDIR /app
ENTRYPOINT ["/bin/bash", "start.sh"]
