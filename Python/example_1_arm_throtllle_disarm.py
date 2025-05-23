from pymavlink import mavutil
import time

# Подключаемся по TCP
IP = "127.0.0.1"

port = 5763
connection_string = f"tcp:{IP}:{port}"  # Заменить на IP дрона
master = mavutil.mavlink_connection(connection_string)

# Ждем первое сообщение heartbeat (важно!)
master.wait_heartbeat()
print(f"Connected to system {master.target_system}, component {master.target_component}")



# 1️ Переводим в режим GUIDED (управляемый полёт)
def set_mode(mode):
    mode_id = master.mode_mapping()[mode]
    master.set_mode(mode_id)
    print(f"Режим изменён на {mode}")

set_mode("GUIDED")

# 2️ Разрешаем моторы (ARM)
master.arducopter_arm()
print("Drone armed!")
time.sleep(2)

# 3️ Взлёт на 2 метра
print("Takeoff to 2 meters...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
    0, 0, 0, 0, 0, 0, 2  # Последний параметр = высота (2 метра)
)

# Ждём набора высоты
time.sleep(5)

# 4 Команда на посадку
print("Landing...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
    0, 0, 0, 0, 0, 0, 0
)

# Ожидание приземления
time.sleep(5)
print("Landed!")

# 5️ Отключаем моторы (DISARM)
master.arducopter_disarm()
print("Drone disarmed!")