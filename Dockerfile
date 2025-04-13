FROM python:3.10

# Set the working directory
WORKDIR /app

# Install system dependencies based on platform
RUN if [ "$(uname -s)" = "Linux" ]; then \
        apt-get update && apt-get install -y libgl1; \
    fi

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["streamlit", "run", "employee_ui.py", "--server.address=0.0.0.0"]
