from pymavlink import mavutil
import time
import signal
import sys

# Подключение по TCP
IP = "127.0.0.1"

port = 5763
connection_string = f"tcp:{IP}:{port}"
master = mavutil.mavlink_connection(connection_string)

# Ждём heartbeat от дрона
master.wait_heartbeat()
print(f"Connected to system {master.target_system}, component {master.target_component}")

# Функция аварийной посадки при выходе через CTRL+C
def emergency_land():
    print("\n[!] Прервано! Выполняем аварийную посадку...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0
    )
    time.sleep(5)
    
    master.arducopter_disarm()
    print("[✔] Дрон разоружён! Завершаем работу.")
    sys.exit(0)

# Перехват SIGINT (CTRL+C)
signal.signal(signal.SIGINT, lambda signum, frame: emergency_land())

# Перевод в режим GUIDED
def set_mode(mode):
    mode_id = master.mode_mapping()[mode]
    master.set_mode(mode_id)
    print(f"Режим изменён на {mode}")

set_mode("GUIDED")

# Разрешаем моторы (ARM)
master.arducopter_arm()
print("Drone armed!")
time.sleep(2)

# Взлёт на 2 метра
print("Takeoff to 2 meters...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
    0, 0, 0, 0, 0, 0, 2  # Высота = 2 метра
)
time.sleep(5)  # Ждём набора высоты

# Проверка поворота на 90° вправо относительно текущего направления
print("Rotating 90 degrees to the right...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
    90,  # Угол поворота (90 градусов)
    10,  # Скорость поворота (10 градусов в секунду)
    1,   # 1 - относительный поворот, 0 - абсолютный
    0, 0, 0, 0
)
time.sleep(5)  # Ждем завершения поворота

# Посадка
print("Landing...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
    0, 0, 0, 0, 0, 0, 0
)
time.sleep(5)

# Отключаем моторы (DISARM)
master.arducopter_disarm()
print("Drone disarmed!")
