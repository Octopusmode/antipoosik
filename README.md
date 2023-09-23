Антипупсиковая нейросистема

## Gstreamer Ubuntu 22.04 LTS

# Установка зависимостей
sudo apt-get install build-essential

sudo apt install ffmpeg

sudo apt install cmake

sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

sudo apt install python3-pip

export PATH="$(echo $HOME)/.local/bin:$PATH"
pip install numpy

# Сборка OpenCV
mkdir ~/opencv_build && cd ~/opencv_build

git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

cd ~/opencv_build/opencv

cmake -D CMAKE_BUILD_TYPE=RELEASE \
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
-D BUILD_EXAMPLES=OFF ..

make -j8

sudo make install