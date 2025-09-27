# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install uvicorn[standard] && \
    pip install .

# Copy the rest of the code
COPY ./backend .

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
