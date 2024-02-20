import requests
import urllib.parse
import json
import psutil
from psutil._common import bytes2human
import time
import signal
import sys
import csv
from datetime import datetime

USER_API_KEY = 'X4HZIY3C1VAUHJFD'
id_del_canal = None
api_key_write = None
cpu_str = ""
ram_str = ""
cont=0
def crear_canal():
    global id_del_canal
    global api_key_write

    print("No existe ningún canal. Creando uno nuevo")
    metodo = 'POST'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host' : 'api.thingspeak.com',
                 'Content-Type' : 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': USER_API_KEY,
              'name' : 'MiCanal',
              'field1' : '%CPU',
              'field2' : '%RAM',
              'public_flag': 1}
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    print(cuerpo_encoded)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo_encoded, allow_redirects=False)

    codigo = respuesta.status_code
    descripcion = respuesta.reason
    print(str(codigo)+ " " + str(descripcion))

    if codigo == 402:
        print("Se ha superado el número máximo de canales permitidos por la cuenta de usuario.\n"
              "Debes borrar un canal en Thingspeak o aumetar tu cuota\n")
        return

    elif codigo == 200:

        cuerpo = respuesta.content
        #print(cuerpo)

        datos = json.loads(cuerpo)
        print(datos)
        id_del_canal = datos["id"]
        lista = datos["api_keys"]
        if lista:
            api_key = lista[0]
        api_key_write = api_key["api_key"]
        print(id_del_canal)
        print(api_key_write)
        guardarEnFichero()
def guardarEnFichero():
    global id_del_canal
    global api_key_write
    with open('datos.txt', 'a') as archivo_txt:
        print(id_del_canal)
        if id_del_canal:
            ids=obtenerIds()
            if id_del_canal is not ids:
                archivo_txt.write(f"ID del canal: {id_del_canal}\n")
                archivo_txt.write(f'API KEY WRITE del canal : {api_key_write}\n')
            else:
                print(f"ID del canal {id_del_canal} ya está presente en el archivo")

def obtenerIds():
    ids=set()
    try:
        with open('datos.txt', 'r') as archivo_txt:
            for linea in archivo_txt:
                if linea.startswith("ID del canal:"):
                    id_del_canal = linea.split(":")[1].strip()
                    ids.add(id_del_canal)
    except:
        pass

    return ids

def canal_existe(id):

    cont = 0
    metodo = 'GET'
    uri = f"https://api.thingspeak.com/channels/{id}.json"
    cabeceras = {'Host': 'api.thingspeak.com', 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': USER_API_KEY}
    respuesta = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)


    if respuesta.status_code == 200:
        cont += 1
        global cont_canal
        cont_canal = cont
        return True
    elif respuesta.status_code == 404:
        return False
    else:
        print(f"Error al verificar la existencia del canal. Código de estado: {respuesta.status_code}")
        return False


def cpu_ram():

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        global cpu_str
        cpu_str = str(cpu)
        global ram_str
        ram_str = str(ram.percent)

def enviar_datos_cpu_ram():

    cpu_ram()
    enviar_pet(cpu_str, ram_str)
    print("CPU: %" + cpu_str + "\tRAM: %" + ram_str)
    time.sleep(15)
def enviar_pet(param1, param2):

    metodo = 'POST'
    uri = "https://api.thingspeak.com/update"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': api_key_write,
              'field1': param1,
              'field2': param2}
    requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)

def limpiar_canal():

    metodo = 'DELETE'
    uri = "https://api.thingspeak.com/channels/" + str(id_del_canal) + "/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com', 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': USER_API_KEY}
    requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)
def obtener_valores():
    metodo = 'GET'
    uri = "https://api.thingspeak.com/channels/" + str(id_del_canal) + "/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com', 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': api_key_write, 'results': 100}
    respuesta = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)

    if respuesta.status_code == 200:
        contenido_json = respuesta.json()
        with open('datos.csv', 'w', newline= '') as csvfile:
            campos = ['timestamp','cpu','ram']
            escritor_csv = csv.DictWriter(csvfile,fieldnames=campos)

            if csvfile.tell() == 0:
                escritor_csv.writeheader()

            for entrada in contenido_json['feeds']:
                timestamp = entrada['created_at']
                cpu = entrada['field1']
                ram = entrada['field2']

                # Convertir la marca de tiempo a un formato legible
                timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

                # Escribir la fila en el archivo CSV
                escritor_csv.writerow({'timestamp': timestamp, 'cpu': cpu, 'ram': ram})



    else:
        print(f"Error al obtener las muestras. Código de estado: {respuesta.status_code}")



def handler(sig_num, frame):
    print('\nSignal handler called with signal' + str(sig_num))
    obtener_valores()
    limpiar_canal()
    print('Check signal number on https://en.wikipedia.org/wiki/Signal_%28IPC%29#Default_action')
    print('\nExiting gracefully')
    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, handler)
    print('Running. Press CTRL-C to exit')
    ids = obtenerIds()
    for id_canal in ids:
        if canal_existe(id_canal):
            print(f"Canal con ID {id_canal} existe. Entonces se utiliza este canal existente")
            id_del_canal = id_canal
            break

    if (cont < 4):
        print("Creating channel...")
        crear_canal()
        print("Channel created. Check on ThingSpeak")
        while True:
            enviar_datos_cpu_ram()
    else:
        print("Se ha superado el número máximo de canales permitidos por la cuenta de usuario.\n"
          "Debes borrar un canal en Thingspeak o aumetar tu cuota\n")

