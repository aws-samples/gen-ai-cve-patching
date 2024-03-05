FROM python:3.10-alpine

ENV LAMBDA_TASK_ROOT="/app/"
ENV AWS_DEFAULT_REGION=us-west-2
ENV USER_ID="APKAQZOY3J3EYI726W6Q"

WORKDIR /app/
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt
RUN apk update && apk add --no-cache git openssh

# Add the host's SSH key to known_hosts to avoid the authenticity prompt
RUN mkdir -p /root/.ssh/ && \
    ssh-keyscan git-codecommit.${AWS_DEFAULT_REGION}.amazonaws.com >> /root/.ssh/known_hosts && \
    echo "Host git-codecommit.*.amazonaws.com" >> /root/.ssh/config && \
    echo "     User ${USER_ID}" >> /root/.ssh/config && \
    echo "     IdentityFile /root/.ssh/id_rsa" >> /root/.ssh/config

COPY keys/id_rsa_git /root/.ssh/id_rsa
COPY main.py ${LAMBDA_TASK_ROOT}   
COPY pr_opener.py ${LAMBDA_TASK_ROOT}  

RUN chmod 400 /root/.ssh/id_rsa
