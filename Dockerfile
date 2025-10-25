FROM python:3.8.0-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV PORT=8000
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT} --reload"]
EXPOSE 8000