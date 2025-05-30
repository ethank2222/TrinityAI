FROM python:3.13

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000


# Use Gunicorn as the production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
