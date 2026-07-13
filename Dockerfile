# Use an official Python slim image as the base
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies first (leverages Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source files
COPY app.py        .
COPY db.py         .
COPY validation.py .

# Expose the default Streamlit port
EXPOSE 8501

# Run Streamlit, disabling the browser-auto-open and ephemeral credentials UI
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--browser.gatherUsageStats=false"]
