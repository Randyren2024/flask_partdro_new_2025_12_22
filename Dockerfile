# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Set work directory
WORKDIR /code

# Install system dependencies if needed (e.g. for some python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

# Copy project
COPY . /code/

# Compile translations
RUN pybabel compile -d translations

# Expose port 9000 (standard for Aliyun FC Custom Container)
EXPOSE 9000

# Start command
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9000", "app:app"]
