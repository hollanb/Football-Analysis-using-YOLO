FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg curl && apt-get clean

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install extra Python packages not listed in requirements.txt
RUN pip install gradio flask

# Copy all local files and folders into the container
COPY . .

# Expose the Gradio port
EXPOSE 7861

# Launch Gradio app
CMD ["python", "gradio_ui.py"]
