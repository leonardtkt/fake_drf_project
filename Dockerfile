FROM python:3.7
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=conf.settings.docker
WORKDIR /code
COPY . /code/
RUN pip install pipenv
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip install -r requirements.txt
