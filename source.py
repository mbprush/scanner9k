import tkinter as tk
from pysnmp.hlapi import *
import os
import win32api
import win32con
import win32gui

# подпрограмма поиска
def find_devices_by_name(ip_address, device_name):
    matching_devices = [] # Создание пустого списка для хранения устройств, соответствующих критериям

    iterator = nextCmd( # Создание итератора для выполнения SNMP запросов
        SnmpEngine(), # Создание объекта SnmpEngine для выполнения запросов
        CommunityData('public', mpModel=0), # Конфигурация SNMP-сообщества и версии протокола
        UdpTransportTarget((ip_address, 161)), # Конфигурация адреса и порта для отправки запросов
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')) # Определение объекта, который будет запрашиваться
    )

# блок ошибок 
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication: # Если возникла ошибка при выполнении запроса
            return matching_devices # Возвращаем список найденных устройств (может быть пустым)
 
        if errorStatus: # Если полученный ответ содержит ошибку
            return matching_devices # Возвращаем список найденных устройств (может быть пустым)
        
#циклично записывает значения в массив VarBind: oid в 0 ид, значение в 1 ид. 
#Проверка сравнивает значения device_name и value: истина переводит значение oid в строку и дописывает его к matching_devices.
#Возвращает читаемое значение value.
        for varBind in varBinds:
            oid = varBind[0] # Получение OID объекта
            value = varBind[1] # Получение значения объекта
            if device_name.lower() in value.prettyPrint().lower(): # Проверка, содержит ли значение объекта заданное имя устройства
                matching_devices.append((str(oid), value.prettyPrint())) # Добавление найденного устройства в список

    return matching_devices # Возвращаем список найденных устройств

# по нажатию кнопки запускается основной блок (функция)
def submit():
    ip_address = input1.get() # Получение значения из виджета input1 (адрес устройства)
    device_name = input2.get() # Получение значения из виджета input2 (имя устройства)
    matching_devices = find_devices_by_name(ip_address, device_name) # Выполнение поиска устройств по заданным критериям
    output_text.delete(1.0, tk.END) # Очистка виджета output_text
    if matching_devices: # Если найдены соответствующие устройства
        output_text.insert(tk.END, f"Совпадения:\n") # Вставка заголовка в виджет output_text
        for oid, name in matching_devices: # Перебор найденных устройств
            output_text.insert(tk.END, f"OID устройства: {oid} | Имя устройства: {name}\n") # Вставка информации об устройстве в виджет output_text
    else:
        output_text.insert(tk.END, f"Не найдено.") # Вывод сообщения о том, что устройства не найдены
    lines = len(output_text.get("1.0", tk.END).split('\n')) # Подсчет количества строк в виджете output_text
    output_text.configure(width=len(output_text.get("1.0", tk.END)) + 2, height=lines) # Конфигурирование размеров виджета output_text

# параметры окна, полей ввода, кнопки и текстового поля
window = tk.Tk() # Создание главного окна приложения
window.title("SNMP Epic Scanner 9000") # Установка заголовка окна
window.geometry("400x250") # Установка размеров окна
window.iconbitmap("iocn.ico") # Установка иконки для окна

hwnd = win32gui.GetParent(window.winfo_id()) # Получение идентификатора окна

icon_path = "iocn.ico" # Путь к файлу иконки
if os.path.exists(icon_path): # Если иконка существует
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE | win32con.LR_SHARED # Флаги для загрузки иконки
    hicon = win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags) # Загрузка иконки
    if hicon: # Если иконка загружена успешно
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon) # Установка иконки для окна
        
input1_label = tk.Label(window, text="Адрес устройства: ") # Создание надписи "Адрес устройства"
input1_label.pack() # Размещение надписи в окне
input1 = tk.Entry(window) # Создание поля ввода для адреса устройства
input1.pack() # Размещение поля ввода в окне

input2_label = tk.Label(window, text="Имя устройства: ") # Создание надписи "Имя устройства"
input2_label.pack() # Размещение надписи в окне
input2 = tk.Entry(window) # Создание поля ввода для имени устройства
input2.pack() # Размещение поля ввода в окне

submit_button = tk.Button(window, text="Ввод", command=submit) # Создание кнопки "Ввод" с привязкой к функции submit
submit_button.pack() # Размещение кнопки в окне

output_label = tk.Label(window) # Создание надписи для вывода результатов
output_label.pack() # Размещение надписи в окне
output_text = tk.Text(window, width=20, height=4) # Создание текстового виджета для вывода результатов
output_text.pack() # Размещение текстового виджета в окне

window.mainloop() # Запуск главного цикла приложения
