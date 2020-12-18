FROM python:3.7-slim-buster as base

FROM base as build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM base

WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY  main.py /app/main.py

ENV PATH="/opt/venv/bin:$PATH"
ENV FLASK_ENV "development"

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]