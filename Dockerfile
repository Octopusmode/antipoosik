FROM python:3.11.5-slim-bullseye

ARG PROJECT_NAME=antipoopsik
ARG GROUP_ID=5000
ARG USER_ID=5000

# Установка зависимостей для сборки OpenCV с поддержкой GStreamer
RUN apt update
RUN apt install -y build-essential --fix-missing
RUN apt install -y ffmpeg --fix-missing
RUN apt install -y cmake
RUN apt install -y libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x \
    gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio \
    python3-dev python3-pip python3-gi python3-gst-1.0 libgirepository1.0-dev libcairo2-dev python3-venv \
    gstreamer1.0-tools gstreamer1.0-plugins-base-apps
RUN apt install -y git
RUN apt -y clean
RUN rm -rf /var/lib/apt/lists/*

# Установка DNS-серверов
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Клонирование репозиториев OpenCV и OpenCV Contrib
RUN git clone https://github.com/opencv/opencv.git && \
    git clone https://github.com/opencv/opencv_contrib.git

# Создание директории для сборки и переход в нее
RUN mkdir /opencv_build && cd /opencv_build

# Установка и сборка OpenCV
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D PYTHON_EXECUTABLE=$(which python3) \
    -D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
    -D BUILD_opencv_python2=OFF \
    -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
    -D PYTHON3_EXECUTABLE=$(which python) \
    -D PYTHON3_INCLUDE_DIR=$(python3 -c "from sysconfig import get_paths as gp; print(gp()[\"include\"])") \
    -D PYTHON3_PACKAGES_PATH=$(python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))") \
    -D WITH_GSTREAMER=ON \
    -D WITH_FFMPEG=ON \
    -D WITH_TBB=OFF \
    -D WITH_CUDA=OFF \
    -D BUILD_EXAMPLES=OFF \
    /opencv

RUN make -j$(nproc)

# Рабочая директория
WORKDIR /app/${PROJECT_NAME}
RUN chown -R ${USER_ID}:${GROUP_ID} /app/${PROJECT_NAME}

# Копирование файлов проекта в рабочую директорию
COPY . /app/${PROJECT_NAME}

# Установка зависимостей проекта
RUN python3 -m pip install --upgrade wheel pip setuptools
RUN python3 -m pip install --no-cache -r requirements.txt

CMD [ "/bin/sleep", "3600" ]

