# Stage A: Build stage for compiling and installing dependencies
FROM python:3.8-slim as builder
WORKDIR /app
COPY requirements.txt .
# Install only the build dependencies required for compiling any necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Stage B: Production stage for creating the final image
FROM python:3.8-slim
WORKDIR /app

# User for better security
RUN groupadd -r django && useradd -r -g django django-user

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt .
# Install the pre-compiled wheels without needing build dependencies
RUN pip install --upgrade pip && pip install --no-cache /wheels/* \
    && pip install newssentiment==1.1.25 --no-deps
COPY . .

RUN chown -R django-user:django /app

USER django-user