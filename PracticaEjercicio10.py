import requests
import urllib.parse
import json
USER_API_KEY = 'X4HZIY3C1VAUHJFD'
id_del_canal = None
api_key_write = None

def create_channel():
    global id_del_canal
    global api_key_write
    ids = obtenerIds()
    for id_canal in ids:
        if canal_existe(id_canal):
            print(f"Canal con ID {id_canal} existe. Entonces se utiliza este canal existente")
            id_del_canal = id_canal
            break
    print("No existe ningún canal. Creando uno nuevo")
    metodo = 'POST'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host' : 'api.thingspeak.com',
                 'Content-Type' : 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': USER_API_KEY,
              'name' : 'MiCanal',
              'field1' : '%CPU',
              'field2' : '%RAM'}
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    print(cuerpo_encoded)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo_encoded, allow_redirects=False)

    codigo = respuesta.status_code
    descripcion = respuesta.reason
    print(str(codigo)+ " " + str(descripcion))

    if codigo == 402 and 'maximum allowed channels reached' in descripcion.lower():
        print("Se ha superado el número máximo de canales permitidos por la cuenta de usuario")
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
    print('aa')
    with open('datos.txt','a') as archivo_txt:
        print('cc')
        print(id_del_canal)
        if id_del_canal:
            print('bbs')
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
    api_url = f"https://api.thingspeak.com/channels/{id}.json"
    respuesta = requests.get(api_url)

    if respuesta.status_code == 200:
        return True
    elif respuesta.status_code == 400:
        return False
    else:
        print(f"Error al verificar la existencia del canal. Código de estado: {respuesta.status_code}")
        return False
if __name__ == "__main__":
    print("Creating channel...")
    create_channel()
    print("Channel created. Check on ThingSpeak")