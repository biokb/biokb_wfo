FROM python:3.13-alpine
WORKDIR /code
COPY src ./src/
COPY pyproject.toml README.md ./
RUN pip install .
#CMD ["fastapi", "run","src/biokb_wfo/api/main.py"]
CMD ["python", "-m", "fastapi", "run", "src/biokb_wfo/api/main.py", "--port", "8000"]
