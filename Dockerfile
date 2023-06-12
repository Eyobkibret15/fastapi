FROM python:3 AS app

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY src/ /app/

ENTRYPOINT python -m app


FROM app AS test

COPY test-requirements.txt /test/
RUN pip install -r /test/test-requirements.txt

COPY test/ /test/

WORKDIR /test

ENTRYPOINT pytest -v
