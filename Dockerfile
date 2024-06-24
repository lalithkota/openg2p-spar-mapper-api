FROM bitnami/python:3.10.13-debian-11-r24

ARG container_user=openg2p
ARG container_user_group=openg2p
ARG container_user_uid=1001
ARG container_user_gid=1001

RUN groupadd -g ${container_user_gid} ${container_user_group} \
  && useradd -mN -u ${container_user_uid} -G ${container_user_group} -s /bin/bash ${container_user}

WORKDIR /app

RUN install_packages libpq-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt/archives

RUN chown -R ${container_user}:${container_user_group} /app

ADD --chown=${container_user}:${container_user_group} . /app/src
ADD --chown=${container_user}:${container_user_group} main.py /app

RUN python3 -m pip install \
  git+https://github.com/openg2p/openg2p-fastapi-common@develop\#subdirectory=openg2p-fastapi-common \
  git+https://github.com/OpenG2P/openg2p-g2pconnect-common-lib@develop\#subdirectory=openg2p-g2pconnect-common-lib \
  git+https://github.com/OpenG2P/openg2p-g2pconnect-common-lib@develop\#subdirectory=openg2p-g2pconnect-mapper-lib \
  ./src

USER ${container_user}

ENV SPAR_MAPPER_WORKER_TYPE=gunicorn
ENV SPAR_MAPPER_HOST=0.0.0.0
ENV SPAR_MAPPER_PORT=8000
ENV SPAR_MAPPER_NO_OF_WORKERS=3

CMD python3 main.py migrate; \
  gunicorn "main:app" --workers ${SPAR_MAPPER_NO_OF_WORKERS} --worker-class uvicorn.workers.UvicornWorker --bind ${SPAR_MAPPER_HOST}:${SPAR_MAPPER_PORT}
