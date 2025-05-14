FROM python:3.11-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CPLUS_INCLUDE_PATH="/usr/include/gdal"
ENV C_INCLUDE_PATH="/usr/include/gdal"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gdal-bin libgdal-dev build-essential python3-dev && \
    apt-get -y autoremove && \
    apt-get clean && rm -rf /var/lib/apt/lists/*  /tmp/* /var/tmp/*

# needed to install numpy before gdal
RUN python3 -m pip install numpy==2.*

# Install other Python dependencies
COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

## Ship code
COPY ecodev_cloud/ /app/ecodev_cloud
WORKDIR /app

#Opened ports
EXPOSE 80

# Set python path
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
