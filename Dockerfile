FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:9001 --chdir=./ --worker-tmp-dir /dev/shm --workers=2 --threads=2 --worker-class=gthread"

CMD ["gunicorn", "main:app"]
