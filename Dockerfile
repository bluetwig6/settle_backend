#
FROM python:3.11.15-trixie

#
WORKDIR /code


COPY requirements.txt ./

#
RUN pip install --no-cache-dir -r requirements.txt

#
COPY . .

#
ENTRYPOINT ["sh", "-c", "alembic upgrade head && exec \"$@\"", "--"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]