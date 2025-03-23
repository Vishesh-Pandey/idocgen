FROM public.ecr.aws/lambda/python:3.8

# Copy your application code into the container
COPY app.py ${LAMBDA_TASK_ROOT}

# Install any dependencies required by your application
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Set the CMD to your handler (could be app.handler if your handler function is named "handler" in "app.py")
CMD ["app.handler"]

