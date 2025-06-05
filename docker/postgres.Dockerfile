FROM postgres:14

# Copy initialization scripts
COPY ./docker-entrypoint-initdb.d /docker-entrypoint-initdb.d

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=smarthome

# Expose the PostgreSQL port
EXPOSE 5432

# Add volume to persist data
VOLUME ["/var/lib/postgresql/data"]
