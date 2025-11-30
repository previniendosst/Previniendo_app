FROM python:3.9-slim AS build-env

# Set environment variables
ENV LANG=es_CO.UTF-8
ENV LC_ALL=es_CO.UTF-8
ENV LC_CTYPE=es_CO.UTF8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV TZ=America/Bogota

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    libpq-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    tzdata \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/America/Bogota /etc/localtime && echo "America/Bogota" > /etc/timezone

# Install python requirements
ARG requirements
COPY ./requirements /tmp/requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/$requirements

# Final stage
FROM build-env
WORKDIR /app
COPY ./ /app
EXPOSE 8000