FROM python:3.10-slim-bookworm

WORKDIR /app

COPY openbb_platform /app/openbb_platform

WORKDIR /app/openbb_platform

RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --extras quant_ml --no-interaction --no-ansi
RUN pip install "./extensions/quant_ml[cache,tracking]"

EXPOSE 6900

ENTRYPOINT ["openbb-api", "--host", "0.0.0.0"]
