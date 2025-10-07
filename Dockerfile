# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, the Python package installer
RUN pip install uv

# Copy the dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv pip install --system -e .

# Copy the rest of the application code
COPY . .

# Environment variables for LeetCode credentials
# These must be provided at runtime
ENV LEETCODE_SESSION=""
ENV LEETCODE_CSRFTOKEN=""

# The command to run the application
ENTRYPOINT ["python", "-m", "run_server"]
