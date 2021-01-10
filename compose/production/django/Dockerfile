
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV POSTGRES_DB=defaultdb
ENV POSTGRES_USER=doadmin
ENV POSTGRES_PASSWORD=htg748qxfybg47vl
ENV POSTGRES_HOST=db-postgresql-nyc1-43047-do-user-8492546-0.b.db.ondigitalocean.com
ENV POSTGRES_PORT=25060
ENV USE_DOCKER=yes

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django . /app

WORKDIR /app

#ENV DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

#RUN python /app/manage.py collectstatic --noinput

#RUN /usr/local/bin/gunicorn config.wsgi --bind 0.0.0.0:5000 --chdir=/app

ENTRYPOINT ["/entrypoint"]