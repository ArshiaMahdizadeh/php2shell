FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tor ca-certificates bash && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-extras.txt /app/
RUN pip install --no-cache-dir -r /app/requirements-extras.txt

COPY php2shell /app/php2shell

RUN printf '#!/usr/bin/env bash\nexec python -m php2shell "$@"\n' > /usr/local/bin/php2shell \
    && chmod +x /usr/local/bin/php2shell

WORKDIR /work
ENTRYPOINT ["php2shell"]