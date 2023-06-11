import tkinter as tk
from pysnmp.hlapi import *

# подпрограмма поиска
def find_devices_by_name(ip_address, device_name):
    matching_devices = []

    iterator = nextCmd( # получение snmp информации
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((ip_address, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr'))
    )

# блок ошибок 
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            return matching_devices

        if errorStatus:
            return matching_devices
        
#циклично записывает значения в массив VarBind: oid в 0 ид, значение в 1 ид. 
#Проверка сравнивает значения device_name и value: истина переводит значение oid в строку и дописывает его к matching_devices.
#Возвращает читаемое значение value.
        for varBind in varBinds:
            oid = varBind[0]
            value = varBind[1]
            if device_name.lower() in value.prettyPrint().lower():
                matching_devices.append((str(oid), value.prettyPrint())) # <-- вот это

    return matching_devices

# по нажатию кнопки запускается основной блок (функция)
def submit():
    ip_address = input1.get()
    device_name = input2.get()
    matching_devices = find_devices_by_name(ip_address, device_name)
    output_text.delete(1.0, tk.END)
    if matching_devices:
        output_text.insert(tk.END, f"Совпадения:\n")
        for oid, name in matching_devices:
            output_text.insert(tk.END, f"OID устройства: {oid} | Имя устройства: {name}\n") #вывод всех подходящих значений
    else:
        output_text.insert(tk.END, f"Не найдено.")
    lines = len(output_text.get("1.0", tk.END).split('\n')) #ширина и высота поля с выводом текста определяется динамически по ширине текста
    output_text.configure(width=len(output_text.get("1.0", tk.END)) + 2, height=lines)

# параметры окна, полей ввода, кнопки и текстового поля
window = tk.Tk()
window.title("SNMP Epic Scanner 9000")
window.geometry("400x250")

input1_label = tk.Label(window, text="Адрес устройства: ")
input1_label.pack()
input1 = tk.Entry(window)
input1.pack()

input2_label = tk.Label(window, text="Имя устройства: ")
input2_label.pack()
input2 = tk.Entry(window)
input2.pack()

submit_button = tk.Button(window, text="Ввод", command=submit)
submit_button.pack()

output_label = tk.Label(window)
output_label.pack()
output_text = tk.Text(window, width=20, height=4)
output_text.pack()

window.mainloop()
