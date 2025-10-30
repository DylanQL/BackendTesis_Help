FROM python:3.12.7-slim

WORKDIR /app

COPY requirements.txt /app/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /entrypoint.sh

# Exponer 8000 porque el runserver va en 8000
EXPOSE 8000

# Copiar entrypoint y dar permisos
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
