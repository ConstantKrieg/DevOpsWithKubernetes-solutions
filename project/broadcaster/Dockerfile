FROM python:3.7-alpine as base

FROM base as build

RUN apk --no-cache add gcc musl-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM base

WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY  main.py /app/main.py

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["python"]
CMD ["main.py"]