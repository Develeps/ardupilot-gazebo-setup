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
print("1️ Takeoff to 2 meters...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
    0, 0, 0, 0, 0, 0, 2
)
time.sleep(5)

#  Функция движения вперёд/назад/влево/вправо
def move(x, y, z, duration=2):
    print(f"Moving to X={x}, Y={y}, Z={z}...")
    master.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            int(0b0000111111000111),  # Управляем только скоростью
            0, 0, 0,  # X, Y, Z (не задаем позицию)
            x, y, z,  # Скорость (X - вперед, Y - вбок, Z - вверх/вниз)
            0, 0, 0,  # Акселерация
            0, 0
        )
    )
    time.sleep(duration)
    print("Stopping movement...")
    master.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            int(0b0000111111000111),
            0, 0, 0,
            0, 0, 0,  # Остановка
            0, 0, 0,
            0, 0
        )
    )
    time.sleep(1)

#  Функция поворота на заданный угол
def rotate(angle):
    print(f"Rotating {angle} degrees...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,
        angle,  # Угол поворота
        10,  # Скорость (градусы в сек)
        1,  # Относительно текущего (1) или абсолютный (0)
        0, 0, 0, 0
    )
    time.sleep(3)

# 2️ Двигаемся вперёд на 1 метр
move(0.5, 0, 0, duration=2)

# 3️ Поворот на 90° вправо
rotate(90)

# 4️ Двигаемся вперёд на 1 метр
move(0.5, 0, 0, duration=2)

# 5️ Поворот на 90° вправо
rotate(90)

# 6️ Двигаемся влево на 1 метр
move(0, -0.5, 0, duration=2)

# 7️ Поворот на 180° (разворот назад)
rotate(180)

# 8️ Двигаемся назад на 1 метр
move(-0.5, 0, 0, duration=2)

# 9️ Плавное снижение на 1 метр
move(0, 0, 0.3, duration=3)

# 10 Посадка
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
