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

#  **Движение вперёд на 1 метр, используя управление скоростью**
print("Moving forward 1 meter...")

# Отправляем команду движения вперед со скоростью 0.5 м/с
master.mav.send(
    mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # Двигаемся в относительных координатах дрона
        int(0b0000111111000111),  # Управляем только скоростью
        0, 0, 0,  # X, Y, Z (не задаем позицию)
        0.5, 0, 0,  # Скорость: X = 0.5 м/с вперёд, Y = 0, Z = 0 (без изменения высоты)
        0, 0, 0,  # Акселерация
        0, 0  # Нулевое ускорение
    )
)

time.sleep(2)  # Даем 2 секунды для движения (примерно 1 м)
print("Stopping movement...")

# Останавливаем дрон (обнуляем скорость)
master.mav.send(
    mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # В той же системе координат
        int(0b0000111111000111),  # Управляем только скоростью
        0, 0, 0,  # X, Y, Z (не задаем позицию)
        0, 0, 0,  # Скорость = 0 (остановка)
        0, 0, 0,  # Акселерация
        0, 0  # Нулевое ускорение
    )
)

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
