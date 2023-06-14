import tkinter as tk
from pysnmp.smi import builder, view
from pysnmp.hlapi import *
import os
import sys
import win32api
import win32con
import win32gui

# Путь к папке с MIB файлами
mib_path = os.path.join(os.getcwd(), 'mibs')

# Установка переменной окружения для поиска MIB файлов
os.environ.setdefault('PYSNMP_MIBS', mib_path)

# Создание экземпляра MIB-построителя
mib_builder = builder.MibBuilder().loadModules('IF-MIB')

# Получение таблицы OID -> имя порта
mib_view_controller = view.MibViewController(mib_builder)
oid_to_port_name = mib_view_controller.getNodeName


def show_port_info():
    port = oid_to_port_name(port_oid)  # Получаем имя порта по OID
    port_oid_str = port_oid.prettyPrint()  # Преобразуем OID в строку
    # Получаем только числовое значение OID
    port_oid_num = '.'.join(map(str, port_oid.asTuple()[1:]))
    output_text.delete(2.0, tk.END)
    output_text.insert(
        tk.END, f"\nИмя порта: {port}\nOID: {port_oid_str}\nOID: {port_oid_num}")
    lines = len(output_text.get("1.0", tk.END).split('\n'))
    output_text.configure(
        width=len(output_text.get("1.0", tk.END)) + 2, height=lines)


def check_port_availability():
    ip_address = ip_entry.get()  # Получаем IP-адрес из поля ввода
    # Получаем коммуникативную строку из поля ввода
    community_string = community_entry.get()
    port = int(port_entry.get())  # Получаем номер порта из поля ввода

    # Формирование SNMP-запроса для получения значения состояния порта
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('IF-MIB', 'ifOperStatus', port)))
    )
    output_text.delete(1.0, tk.END)
    if error_indication:
        output_text.insert(tk.END, f"Ошибка: " + str(error_indication))
    elif error_status:
        output_text.insert(tk.END, f"Ошибка: " +
                           str(error_status.prettyPrint()))
    else:
        for var_bind in var_binds:
            if var_bind[1] == 1:  # 1 соответствует активному состоянию порта
                global port_oid
                port_oid = var_bind[0]  # Запоминаем OID порта
                # port = oid_to_port_name(var_bind[0])  # Получаем имя порта по OID
                output_text.insert(
                    tk.END, f"Порт {port} на устройстве {ip_address} доступен.")
                # Активируем кнопку для показа информации
                show_info_button.config(state=tk.NORMAL)
                reboot_button.config(state=tk.DISABLED)
            else:
                output_text.insert(
                    tk.END, f"Порт {port} на устройстве {ip_address} недоступен.")
                # Отключаем кнопку для показа информации
                show_info_button.config(state=tk.DISABLED)
                reboot_button.config(state=tk.NORMAL)  # Разблокировать кнопку "Перезагрузить маршрутизатор"
            lines = len(output_text.get("1.0", tk.END).split('\n'))
            output_text.configure(
                width=len(output_text.get("1.0", tk.END)) + 2, height=lines)

def reboot_router():
    ip_address = ip_entry.get()  # Получаем IP-адрес из поля ввода
    # Получаем коммуникативную строку из поля ввода
    community_string = community_entry.get()
    port = int(port_entry.get())  # Получаем номер порта из поля ввода
    # Формирование SNMP-запроса для отправки сигнала перезагрузки маршрутизатору
    error_indication, error_status, error_index, var_binds = next(
        setCmd(SnmpEngine(),
               CommunityData(community_string),
               UdpTransportTarget((ip_address, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'snmpTrapOID'), '0.0'),
               ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'), Integer(2)))
    )

    if error_indication:
        output_text.insert(
                    tk.END, f"\nОшибка: ", error_indication)
    elif error_status:
        output_text.insert(
                    tk.END, f"\nОшибка: ", error_status.prettyPrint())
    else:
        output_text.insert(
                    tk.END, f"\nСигнал перезагрузки маршрутизатора отправлен.")

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
icon_path = os.path.join(data_folder, 'iocn.ico')

# Создание графического интерфейса
window = tk.Tk()
window.title("Проверка доступности порта")
window.geometry("400x250")

ip_label = tk.Label(window, text="IP-адрес:")
ip_label.pack()
ip_entry = tk.Entry(window)
ip_entry.pack()

community_label = tk.Label(window, text="Коммуникативная строка:")
community_label.pack()
community_entry = tk.Entry(window)
community_entry.pack()

port_label = tk.Label(window, text="Номер порта:")
port_label.pack()
port_entry = tk.Entry(window)
port_entry.pack()

check_button = tk.Button(window, text="Проверить",
                         command=check_port_availability)
check_button.pack()

output_label = tk.Label(window)
output_label.pack()
output_text = tk.Text(window, width=20, height=4)
output_text.pack()

show_info_button = tk.Button(
    window, text="Показать информацию", state=tk.DISABLED, command=show_port_info)
show_info_button.pack()

reboot_button = tk.Button(
    window, text="Отправить команду перезагрузки", state=tk.DISABLED, command=reboot_router)
reboot_button.pack()

port_info_label = tk.Label(window, text="")

window.mainloop()
