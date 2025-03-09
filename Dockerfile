FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Исключаем ненужные файлы и директории
RUN find . \( -name ".git" -o -name ".gitignore" -o -name "README.md" \) -prune -exec rm -rf {} \;

RUN chmod +x /app/docker/entrypoint.sh

VOLUME /data

ENTRYPOINT ["/app/docker/entrypoint.sh"]