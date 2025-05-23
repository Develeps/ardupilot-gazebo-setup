#!/bin/bash

set -e  # Останавливаем выполнение при ошибке

echo "Начало установки Gazebo и ArduPilot SITL..."

# === 1. Обновление системы ===
echo "Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# === 2. Установка Python3 и pip ===
echo "Устанавливаем Python3 и pip..."
sudo apt install -y python3 python3-pip python-is-python3

# === 3. Установка зависимостей через APT ===
echo "Устанавливаем APT-зависимости..."
sudo apt install -y git python3-dev python3-setuptools python3-wheel python3-pyparsing \
python3-matplotlib python3-lxml python3-pandas python3-scipy python3-pyqt5 python3-pyqtgraph \
python3-pil python3-future python3-msgpack python3-yaml python3-pyudev python3-cbor python3-dateutil \
python3-tk python3-pyshp python3-pygame python3-pyglet python3-psutil python3-pexpect python3-ruamel.yaml \
lsb-release wget gnupg

# === 4. Установка недостающих Python-библиотек через pip ===
echo "Устанавливаем Python-зависимости через pip..."
pip install --user --upgrade pyserial pymavlink pynmea2 pyquaternion

# Добавляем pip-библиотеки в PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# === 5. Установка MAVProxy ===
echo "Устанавливаем MAVProxy..."
pip install --user pymavlink MAVProxy

# === 6. Установка Gazebo (Harmonic) ===
echo "Устанавливаем Gazebo Harmonic..."
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install -y gz-harmonic

# === 7. Установка ArduPilot ===
echo "Клонируем ArduPilot..."
cd ~
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# === 8. Установка зависимостей для сборки ArduPilot ===
echo "Устанавливаем зависимости для ArduPilot..."
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile

# === 9. Сборка ArduPilot SITL ===
echo "Компилируем ArduPilot SITL..."
./waf configure --board sitl
./waf copter

# === 10. Установка плагина ArduPilot для Gazebo ===
echo "Устанавливаем плагин ArduPilot для Gazebo..."
sudo apt install -y libgz-sim8-dev rapidjson-dev libopencv-dev libgstreamer1.0-dev \
libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl

mkdir -p ~/gz_ws/src && cd ~/gz_ws/src
git clone https://github.com/ArduPilot/ardupilot_gazebo
cd ardupilot_gazebo
mkdir build && cd build
export GZ_VERSION=harmonic
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)

# === 11. Добавление переменных среды ===
echo "Настраиваем переменные среды..."
echo 'export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/gz_ws/src/ardupilot_gazebo/build:${GZ_SIM_SYSTEM_PLUGIN_PATH}' >> ~/.bashrc
echo 'export GZ_SIM_RESOURCE_PATH=$HOME/gz_ws/src/ardupilot_gazebo/models:$HOME/gz_ws/src/ardupilot_gazebo/worlds:${GZ_SIM_RESOURCE_PATH}' >> ~/.bashrc
source ~/.bashrc

# === 12. Проверка наличия sim_vehicle.py ===
echo "Проверяем наличие sim_vehicle.py..."
if ! command -v sim_vehicle.py &> /dev/null
then
    echo "sim_vehicle.py не найден, добавляем в PATH..."
    ln -s ~/ardupilot/Tools/autotest/sim_vehicle.py ~/.local/bin/sim_vehicle.py
    source ~/.bashrc
fi

echo "Установка завершена! Теперь можно запустить симуляцию."

# # === 13. Запуск симуляции ===
# read -p "Хотите запустить симуляцию прямо сейчас? (y/n): " answer
# if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
#     echo "Запускаем Gazebo..."
#     gz sim -v4 -r iris_runway.sdf &

#     sleep 5

#     echo "Запускаем ArduPilot SITL..."
#     cd ~/ardupilot/ArduCopter
#     sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
# fi

echo "Установка и настройка завершены!"
