FROM python:latest
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
WORKDIR /code
COPY ./app ./app
CMD uvicorn app.main:app --host=0.0.0.0 --port=8585
EXPOSE 8585
