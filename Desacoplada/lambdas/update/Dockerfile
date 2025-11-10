FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
COPY app/ ./app/

# Copiamos el código de esta función
COPY lambdas/update ./


RUN pip install --no-cache-dir -r requirements.txt --target .

CMD ["app.handler"]