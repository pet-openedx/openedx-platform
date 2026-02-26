FROM python:3.11-slim-bookworm AS python-build

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    build-essential \
    git \
    default-libmysqlclient-dev \
    libxmlsec1-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/edx/base.txt /tmp/base.txt
RUN pip install --prefix=/install -r /tmp/base.txt


FROM node:20-bookworm AS assets-build

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json package-lock.json ./
COPY scripts/ ./scripts/
RUN npm ci --no-audit

COPY requirements/edx/assets.txt /tmp/assets.txt
RUN pip3 install --break-system-packages -r /tmp/assets.txt

COPY . .
RUN npm run build


FROM python:3.11-slim-bookworm AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    libxmlsec1-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build /install /usr/local

WORKDIR /app

COPY . .
COPY --from=assets-build /app/lms/static ./lms/static
COPY --from=assets-build /app/cms/static ./cms/static
COPY --from=assets-build /app/common/static ./common/static

ENV DJANGO_SETTINGS_MODULE=lms.envs.production

EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "lms.wsgi:application"]
