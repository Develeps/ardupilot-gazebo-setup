# 🛰️ ardupilot-gazebo-setup

Скрипт для автоматической установки среды симуляции ArduPilot SITL и Gazebo Harmonic на Ubuntu 22.04.  
Работает как в обычной Linux-среде, так и в **WSL2** (Windows Subsystem for Linux) с **встроенной поддержкой GUI (WSLg)** — без необходимости устанавливать X-сервер.

---

## ⚙️ Возможности

- Установка всех необходимых APT и pip-зависимостей
- Клонирование и компиляция ArduPilot (ArduCopter SITL)
- Установка Gazebo Harmonic и плагина `ardupilot_gazebo`
- Настройка переменных окружения
- Возможность автоматического запуска симуляции по завершению установки

---

## 🖥 Поддерживаемая среда

- **Ubuntu 22.04 LTS**
- **WSL2 + WSLg**  
  (Windows 10 19045+ / Windows 11 — GUI-приложения работают из коробки)

> ✅ Не требуется отдельный X-сервер (VcXsrv, Xming и т.д.)  
> ✅ Проверено на: Microsoft Windows [Version 10.0.19045.2965]

---

## 🚀 Установка

```bash
git clone https://github.com/Develeps/ardupilot-gazebo-setup.git
cd ardupilot-gazebo-setup
chmod +x install_ardupilot_gazebo.sh
./install_ardupilot_gazebo.sh
```