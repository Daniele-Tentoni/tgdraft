FROM python:3.9

WORKDIR /code

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

ENV PATH="${PATH}:${HOME}/.poetry/bin/"

RUN ${HOME}/.poetry/bin/poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN ${HOME}/.poetry/bin/poetry install --no-interaction --no-ansi --no-dev

COPY tgdraft /code/tgdraft

CMD ["python", "-m", "tgdraft"]
