FROM python:3.11.5-slim-bullseye

ARG PROJECT_NAME=antipoopsik
ARG GROUP_ID=5000
ARG USER_ID=5000

RUN apt update
RUN apt install -y python3-dev python3-pip python3-gi python3-gst-1.0 libgirepository1.0-dev libcairo2-dev

RUN groupadd --gid ${GROUP_ID} ${PROJECT_NAME}
RUN useradd --uid ${USER_ID} --gid ${USER_ID} --shell /bin/sh -m --skel /dev/null /app/${PROJECT_NAME}
WORKDIR /app/${PROJECT_NAME}
RUN chown -R ${USER_ID}:${GROUP_ID} /app/${PROJECT_NAME}

ENV VIRTUAL_ENV=/app/${PROJECT_NAME}/.venv
ENV PATH="$VIRTUAL_ENV/bin:${PATH}"
ENV PYTHONPATH=/app/${PROJECT_NAME}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/${PROJECT_NAME}

RUN python3 -m pip install --upgrade wheel pip setuptools
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV
RUN python3 -m pip install --no-cache -r requirements.txt

USER ${REMOTE_USER}

CMD [ "/bin/sleep", "3600" ]
