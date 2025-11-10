FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

COPY app/ ./app/
COPY requirements.txt .

# Copiamos el código de esta función
COPY lambdas/delete ./

RUN pip install --no-cache-dir -r requirements.txt --target .

CMD ["app.handler"]