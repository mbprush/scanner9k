from tkinter import * # 
from pysnmp.hlapi import *
import tkinter as tk

# Функция для проверки доступности порта
def check_port():
    ip = ip_entry.get() # Получение значения из виджета ip_entry.
    community = community_entry.get() # Получение значения из виджета community_entry
    port = int(port_entry.get()) # Получение значения из виджета port_entry и преобразование в целое число
    result_text.delete(1.0, tk.END) # Удаление текста из виджета result_text, начиная с позиции 1.0 до конца
    result_label.config(text="") # Установка пустого значения для текста в виджете result_label
    admin_status_oid = f"1.3.6.1.2.1.2.2.1.7.{port}" # Формирование OID для административного статуса порта
    oper_status_oid = f"1.3.6.1.2.1.2.2.1.8.{port}" # Формирование OID для операционного статуса порта

    # Получение значения административного статуса порта с помощью SNMP
    admin_status_error_indication, admin_status_error_status, admin_status_error_index, admin_status_var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(admin_status_oid)))
    )
    
    # Получение значения операционного статуса порта с помощью SNMP
    oper_status_error_indication, oper_status_error_status, oper_status_error_index, oper_status_var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oper_status_oid)))
    )

    # Проверка на наличие ошибки при получении административного статуса порта
    if admin_status_error_indication:
        result_label.config(text=f"Ошибка при получении статуса порта {port}: {admin_status_error_indication}")
        return

    # Проверка на наличие ошибки при получении операционного статуса порта
    if oper_status_error_indication:
        result_label.config(text=f"Ошибка при получении операционного статуса порта {port}: {oper_status_error_indication}")
        return

    admin_status = admin_status_var_binds[0][1] # Извлечение значения административного статуса из полученных данных
    oper_status = oper_status_var_binds[0][1] # Извлечение значения операционного статуса из полученных данных

    # Проверка доступности порта на роутере
    if admin_status == 1 and oper_status == 1: 
        result_text.insert(tk.END, f"Порт {port} доступен на роутере {ip}\n") # Вставка информации о доступном порте в виджет result_text
        lines = len(result_text.get("1.0", tk.END).split('\n')) # Подсчет количества строк в виджете result_text
        result_text.configure(
                width=len(result_text.get("1.0", tk.END)) + 2, height=lines) # Изменение размеров виджета result_text в соответствии с количеством строк
    else:
        result_text.insert(tk.END, f"Порт {port} недоступен на роутере {ip}\n") # Вставка информации о недоступном порте в виджет result_text
        lines = len(result_text.get("1.0", tk.END).split('\n')) # Подсчет количества строк в виджете result_text
        result_text.configure(
                width=len(result_text.get("1.0", tk.END)) + 2, height=lines) # Изменение размеров виджета result_text в соответствии с количеством строк
        decode_oper_status(oper_status) # Декодирование операционного статуса порта
        reboot_router(ip, community) # Перезагрузка роутера
        
# Функция для перезагрузки устройства (Роутер MikroTik RouterBoard)
def reboot_router(ip, community):
    # Отправка команды перезагрузки на роутер с помощью SNMP
    error_indication, error_status, error_index, var_binds = next(
        setCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('1.3.6.1.4.1.14988.1.1.7.1.0'), OctetString('1')))
    )

    if error_indication: # Проверка на наличие ошибки при отправке команды перезагрузки
        result_text.insert(tk.END, f"Ошибка: {error_indication}")
    else:
        result_text.insert(tk.END, f"Отправлена команда перезагрузки на роутер {ip}")   

# Функция для декодирования значения операционного статуса порта (ifOperStatus)
def decode_oper_status(status):
    # Декодирование значения операционного статуса порта и установка соответствующего текста в виджете result_label
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
root = Tk() # Создается объект класса Tk и присваивается переменной root. Этот объект представляет главное окно приложения.
root.title("Проверка доступности порта") # Устанавливается заголовок главного окна.
root.geometry("300x250") # Устанавливается размеры главного окна.

# Поле ввода IP-адреса
ip_label = Label(root, text="IP-адрес роутера:") # Создается виджет Label (подпись) и привязывается к главному окну. Виджет отображает текст "IP-адрес роутера:".
ip_label.pack() # Располагает виджет ip_label в главном окне.
ip_entry = Entry(root) # Создается виджет Entry (поле ввода) и привязывается к главному окну.
ip_entry.pack() # Располагает виджет ip_entry в главном окне.

# Поле ввода коммуникативной строки
community_label = Label(root, text="Community:") Создается виджет Label и привязывается к главному окну. Виджет отображает текст "Community:".
community_label.pack() # Располагает виджет community_label в главном окне.
community_entry = Entry(root) # Создается виджет Entry и привязывается к главному окну.
community_entry.pack() # Располагает виджет community_entry в главном окне.

# Поле ввода номера порта
port_label = Label(root, text="Номер порта:") # Создается виджет Label и привязывается к главному окну. Виджет отображает текст "Номер порта:".
port_label.pack() # Располагает виджет port_label в главном окне.
port_entry = Entry(root) # Создается виджет Entry и привязывается к главному окну.
port_entry.pack() # Располагает виджет port_entry в главном окне.

# Кнопка для проверки доступности порта
check_button = Button(root, text="Проверить", command=check_port) # Создается виджет Button (кнопка) и привязывается к главному окну. Виджет отображает текст "Проверить" и при нажатии вызывает функцию check_port.
check_button.pack() # Располагает виджет check_button в главном окне.

# Поле для вывода результата
result_label = Label(root) # Создается виджет Label и привязывается к главному окну.
result_label.pack() # Располагает виджет result_label в главном окне.
result_text = tk.Text(root, width=20, height=4) # Создается виджет Text (текстовое поле) и привязывается к главному окну. Устанавливаются размеры поля: ширина - 20 символов, высота - 4 строки.
result_text.pack() #  Располагает виджет result_text в главном окне.

root.mainloop() # Запускается главный цикл обработки событий приложения. Он ожидает и обрабатывает действия пользователя, такие как нажатие кнопок и ввод данных в поля.
