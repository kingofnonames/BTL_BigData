FROM python:3.11-slim
WORKDIR /app/speed

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Let the container run the speed.py script by default(Changable if needed)
CMD ["python", "speed.py"]