FROM python:3.11

# RUN apt update && \
#     apt install -y \
#     python3.9-dev \

RUN apt update && \
    apt install -y \
    python3-dev \
    python3-pip \
    # autoconf automake libtool \
    python3-gi \
    python3-gst-1.0 \
    libgirepository1.0-dev \
    libcairo2-dev

RUN pip install --upgrade wheel pip setuptools

RUN pip install pycairo

RUN pip install PyGObject

CMD [ "/bin/sleep", "3600" ]
