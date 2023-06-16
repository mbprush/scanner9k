from tkinter import *
from pysnmp.hlapi import *
import tkinter as tk

# Функция для проверки доступности порта
def check_port():
    ip = ip_entry.get()
    community = community_entry.get()
    port = int(port_entry.get())
    result_text.delete(1.0, tk.END)
    result_label.config(text="")
    admin_status_oid = f"1.3.6.1.2.1.2.2.1.7.{port}"
    oper_status_oid = f"1.3.6.1.2.1.2.2.1.8.{port}"

    admin_status_error_indication, admin_status_error_status, admin_status_error_index, admin_status_var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(admin_status_oid)))
    )

    oper_status_error_indication, oper_status_error_status, oper_status_error_index, oper_status_var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oper_status_oid)))
    )

    if admin_status_error_indication:
        result_label.config(text=f"Ошибка при получении статуса порта {port}: {admin_status_error_indication}")
        return

    if oper_status_error_indication:
        result_label.config(text=f"Ошибка при получении операционного статуса порта {port}: {oper_status_error_indication}")
        return

    admin_status = admin_status_var_binds[0][1]
    oper_status = oper_status_var_binds[0][1]

    if admin_status == 1 and oper_status == 1:
        result_text.insert(tk.END, f"Порт {port} доступен на роутере {ip}\n")
        lines = len(result_text.get("1.0", tk.END).split('\n'))
        result_text.configure(
                width=len(result_text.get("1.0", tk.END)) + 2, height=lines)
    else:
        result_text.insert(tk.END, f"Порт {port} недоступен на роутере {ip}\n")
        lines = len(result_text.get("1.0", tk.END).split('\n'))
        result_text.configure(
                width=len(result_text.get("1.0", tk.END)) + 2, height=lines)
        decode_oper_status(oper_status)
        reboot_router(ip, community)

def reboot_router(ip, community):
    error_indication, error_status, error_index, var_binds = next(
        setCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('1.3.6.1.4.1.14988.1.1.7.1.0'), OctetString('1')))
    )

    if error_indication:
        result_text.insert(tk.END, f"Ошибка: {error_indication}")
    else:
        result_text.insert(tk.END, "Отправлена команда перезагрузки на роутер {ip}")   

# Функция для расшифровки уровней доступности (ifOperStatus)
def decode_oper_status(status):
    if status == 1:
        result_label.config(text="Уровень доступности по ifOperStatus: Up (1)")
    elif status == 2:
        result_label.config(text="Уровень доступности по ifOperStatus: Down (2)")
    elif status == 3:
        result_label.config(text="Уровень доступности по ifOperStatus: Testing (3)")
    elif status == 4:
        result_label.config(text="Уровень доступности по ifOperStatus: Unknown (4)")
    elif status == 5:
        result_label.config(text="Уровень доступности по ifOperStatus: Dormant (5)")
    elif status == 6:
        result_label.config(text="Уровень доступности по ifOperStatus: NotPresent (6)")
    elif status == 7:
        result_label.config(text="Уровень доступности по ifOperStatus: LowerLayerDown (7)")
    else:
        result_label.config(text=f"Уровень доступности по ifOperStatus: Неизвестный ({status})")

# Создание графического интерфейса
root = Tk()
root.title("Проверка доступности порта")
root.geometry("300x250")

# Поле ввода IP-адреса
ip_label = Label(root, text="IP-адрес роутера:")
ip_label.pack()
ip_entry = Entry(root)
ip_entry.pack()

# Поле ввода community
community_label = Label(root, text="Community:")
community_label.pack()
community_entry = Entry(root)
community_entry.pack()

# Поле ввода номера порта
port_label = Label(root, text="Номер порта:")
port_label.pack()
port_entry = Entry(root)
port_entry.pack()

# Кнопка для проверки доступности порта
check_button = Button(root, text="Проверить", command=check_port)
check_button.pack()

# Метка для вывода результата
result_label = Label(root)
result_label.pack()
result_text = tk.Text(root, width=20, height=4)
result_text.pack()

root.mainloop()
