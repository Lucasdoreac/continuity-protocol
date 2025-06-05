FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p data/sessions data/contexts data/llmops/timesheets data/llmops/sprints data/llmops/reports logs

# Set environment variables
ENV PYTHONPATH=/app
ENV LOGLEVEL=INFO

# Expose port for HTTP server
EXPOSE 8000

# Default command (HTTP server)
CMD ["python", "-m", "continuity_protocol.server", "--name", "Continuity-Protocol-Docker", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]

# Alternative command for stdio transport (commented out)
# CMD ["python", "-m", "continuity_protocol.server", "--name", "Continuity-Protocol-Docker", "--transport", "stdio"]