FROM python:3.12-bookworm
ENV PYTHONUNBUFFERED=1

RUN apt-get install -yqq libpq-dev
RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pip
RUN pip install -U pip setuptools
RUN pip install poetry==1.8.3

COPY poetry.lock pyproject.toml /code/
RUN pip3 cache purge
RUN poetry env use system
RUN poetry config virtualenvs.create false
RUN poetry lock --no-update
RUN poetry install --no-interaction --no-ansi

COPY . /code/

CMD ["mkdocs", "serve"]