FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --uid 10001 chocowise \
    && chown chocowise:chocowise /app
COPY --chown=chocowise:chocowise app/ ./app/
COPY --chown=chocowise:chocowise FAQ.json inventory.json ./

USER chocowise
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
