FROM python:3

COPY app.py .
COPY ../requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]