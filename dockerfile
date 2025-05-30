FROM python:3.13
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install huggingface_hub[hf_xet]

COPY . .
EXPOSE 8000


# Use Gunicorn as the production server
CMD ["python", "app.py"]