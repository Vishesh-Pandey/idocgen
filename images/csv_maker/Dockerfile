FROM public.ecr.aws/lambda/python:3.12.2025.03.21.14

# Install Git using dnf (Amazon Linux 2023 uses dnf instead of yum)
RUN dnf install -y git

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install swarm separately from GitHub
# RUN pip install --no-cache-dir git+https://github.com/openai/swarm.git

# Copy application code into the container
COPY src/* ${LAMBDA_TASK_ROOT}

# Set the CMD to your Lambda function handler
CMD ["main.handler"]
