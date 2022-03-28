from asyncio.windows_events import NULL
from cProfile import label
from cgitb import text
# from cgi import print_directory
# from cgitb import text
# from faulthandler import disable
# from importlib.resources import path
# from pyexpat import model
# from textwrap import fill
from tkinter import *
from tkinter import font
from tkinter.filedialog import askopenfile
import tkinter
from turtle import left, width
from click import command
from flask import jsonify
# from turtle import left, position
# from unicodedata import name
# from numpy import empty
import pyaudio
import pyttsx3
import speech_recognition as sr
from difflib import SequenceMatcher as SM
from pydub import AudioSegment
from pydub.silence import split_on_silence
import shutil
import os
#date
import MySQLdb
from datetime import date
import threading
import glob
import wave

conn = MySQLdb.connect(host="bj2wi6com0g9o1zjkchn-mysql.services.clever-cloud.com",port=3306,user="upbgfedtmnbjjika",passwd="SWdkwcjXD3dEqILd8EmB",db="bj2wi6com0g9o1zjkchn")

# confiracion del microfono
recognizer = sr.Recognizer()

eng = pyttsx3.init()

eng.setProperty("rate",140)

eng.setProperty("volume",1.0)

listVoices = eng.getProperty("voices")
eng.setProperty("voice",listVoices[0].id)


#ventana2
ventana = None
time = None
cedula = NULL


#VARIABLES INICIALES
grabando=False
reproduciendo=False
CHUNK=1024
data=""
stream=""
audio=pyaudio.PyAudio()
f=""

status_modo=None
status_microfono_archivo = None


# Conexion Mysql
def Insert_mysql(text):

    print("palabra", text)
    print("Cedula",cedula)

    try:
        cursor_mysql = conn.cursor()
        query_insert="insert into Registro(cedula,registro,fecha) VALUES (%s,%s,%s)"
        values = (cedula),str(text),str(date.today().strftime("%Y/%m/%d"))
        cursor_mysql.execute(query_insert,values)
        conn.commit()

        time['text']="Finalizacion correcta"
        print("Sucess")
    except:
        time['text']="Fallo inesperado"
        print("Fail")

def getdatos(cedula):
    try:
        arraydatos = []

        cursormysql = conn.cursor() 
        cursormysql.execute(f"select * from Registro where cedula={cedula}")
        rowdata= cursormysql.fetchall()
        resultados=[]
        for i in rowdata:
            valor={'cedula':i[0],'registro':i[1],'fecha':i[2]}
            resultados.append(valor)
        registro= resultados[0]['registro']
        registro= registro.lower()
        registro= registro.split(" ")
    
        palabras_claves1= {"uenos":0,"buenos":0, "buenas":0, "buen":0,"llenamos":0,"llenar":0,"aditivo":0,"cero":0,"ceros":0,"soat":0,"obsequiando": 0, "extintor":0,"finalizado":0,"terminado":0,"garantizamos":0}

        for i in registro:
            if i in palabras_claves1:
                palabras_claves1[i] +=1

        # print(palabras_claves1)
        val = str(max(palabras_claves1.items(), key=lambda x: x[1])[0])
        saludos= palabras_claves1[val]
        llenados= palabras_claves1["llenar"]+palabras_claves1["llenamos"]
        
        if saludos<=llenados:
            arraydatos.append("ofreció llenar el tanque a todos los cliente(s)")
        else:
            arraydatos.append("le faltó por ofrecer  llenar el tanque a",saludos-llenados," cliente(s)")

        if saludos<=palabras_claves1["aditivo"]:
            arraydatos.append("ofreció aditivo a todos los cliente(s)")
        else:
            arraydatos.append(f"le faltó por ofrecer  aditivo  a {saludos-palabras_claves1['aditivo']} cliente(s)")

        if saludos<=palabras_claves1["soat"]:
            arraydatos.append("ofreció el SOAT a todos los cliente(s)")
        else:
            arraydatos.append(f"le faltó por ofrecer  el SOAT  a {saludos-palabras_claves1['soat']} cliente(s)")

        if saludos<=palabras_claves1["ceros"]+palabras_claves1["cero"]:
            arraydatos.append("indicó que la maquina estaba en ceros a todos los cliente(s)")
        else:
            arraydatos.append(f"le faltó indicar que la maquina estaba en cero a {saludos-palabras_claves1['ceros']+palabras_claves1['cero']} cliente(s)")

        if saludos<=palabras_claves1["extintor"]:
            arraydatos.append("ofreció recargar el extintor  a todos los clientes")
        else:
            arraydatos.append(f"le faltó por ofrecer  recargar el extintor a {saludos-palabras_claves1['extintor']} cliente(s)")

        return (arraydatos)
    except:
        return 'Error'

# Abrir inspeccion de archivos
def open_file(): 
    file = askopenfile(mode ='r', filetypes =[('War files', '*.wav')])
    if file is not None:
        return str(file.name)

def formato(c):
    if c<10:
        c="0"+str(c)
    return c

def clear_contador():
    global contador,contador1,contador2
    time['text'] = "0:00:00"
    contador=0
    contador1=0
    contador2=0

def cuenta():
    global proceso
    global contador,contador1,contador2
    time['text'] = str(contador1)+":"+str(formato(contador2))+":"+str(formato(contador))
    contador+=1
    if contador==60:
        contador=0
        contador2+=1
    if contador2==60:
        contador2=0
        contador1+=1
    proceso=time.after(1000, cuenta)


def grabacion(FORMAT,CHANNELS,RATE,CHUNK,audio,archivo):
    
    stream=audio.open(format=FORMAT,channels=CHANNELS,
                          rate=RATE, input=True,
                          frames_per_buffer=CHUNK)

    frames=[]

    while grabando==True:
        data=stream.read(CHUNK)
        frames.append(data)

    #DETENEMOS GRABACIÓN
    stream.stop_stream()
    stream.close()
    audio.terminate()

    grabs = glob.glob('*.mp3')

    #CREAMOS/GUARDAMOS EL ARCHIVO DE AUDIO
    count=0
    for i in grabs:
        if "grabacion" in i:
            count+=1
    if count>0:
        archivo="grabacion"+"("+str(count)+")"+".wav"
        
    waveFile = wave.open(archivo, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    modes(archivo)

def parar():
    global grabando
    global reproduciendo
    if grabando==True:
        grabando=False
        time.after_cancel(proceso)
        clear_contador()
    elif reproduciendo==True:
        reproduciendo=False


def iniciar():
    global grabando
    global proceso
    global act_proceso
    clear_contador()
    audio=pyaudio.PyAudio()
    grabando=True
    FORMAT=pyaudio.paInt16
    CHANNELS=2
    RATE=44100
    act_proceso=True
    archivo="grabacion.wav"
    t1=threading.Thread(target=grabacion, args=(FORMAT,CHANNELS,RATE,CHUNK,audio,archivo))
    t=threading.Thread(target=cuenta)
    t1.start()
    t.start()


def recognizen(fuente=None):

    origen = sr.AudioFile(fuente)

    with origen as source:

        audio = recognizer.record(source)

        try:
            return recognizer.recognize_google(audio,language="es-Es")
        except sr.UnknownValueError:
            return ' '

def modes(archive):

    palabra = ""

    foldername = "ListaAudios"

    print("Leyendo archivo ....")


    if archive == None:
        url = open_file()
        time['text']="Cargando datos ...."
    else:
        url = archive

    sound = AudioSegment.from_wav(url)

    chunks = split_on_silence(sound,min_silence_len=500,silence_thresh=sound.dBFS-14,keep_silence=500)

    for i, audio_chunk in enumerate(chunks, start=1):

        chunk_filename = os.path.join(foldername, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        respuesta = recognizen(chunk_filename)

        if respuesta != ' ':
            text = f"{respuesta}\t"
            palabra += text
                
    Insert_mysql(palabra)
    print(palabra.capitalize())
    return palabra

def ventana2():
    global status_modo
    if(status_microfono_archivo):
        ventana_file.destroy()
    elif(status_microfono_archivo == False):
        ventana_microfono.destroy()
    else:
        vistaPrinc.destroy()

    status_modo = False

    global ventana
    ventana = tkinter.Tk()
    ventana.geometry("600x600")
    ventana.title("Reconocimiento de voz")
    etiqueta = tkinter.Label(ventana, text="Reconocimiento de voz",font=25)
    etiqueta.pack(padx=5,pady=5,ipadx=5,ipady=5)
    back_button = tkinter.Button(ventana,bg="red",fg="white",text="Atras",command=vista_princ)
    back_button.place(x=4,y=4,width=50,height=30)

    boton1 = tkinter.Button(ventana, text="Microfono",bg="green",fg="white",command=microphone)
    boton1.place(x=70,y=280,width=100,height=60)

    boton2 = tkinter.Button(ventana, text="Cargar archivo",bg="green",fg="white",command=file_upload)
    boton2.place(x=440,y=280,width=100,height=60)

    ventana.mainloop()

    foldername = "ListaAudios"

    if os.path.isdir(foldername):
        shutil.rmtree(foldername)

    os.mkdir(foldername)


def microphone():
    global status_microfono_archivo
    ventana.destroy()
    status_microfono_archivo = False
    global ventana_microfono
    ventana_microfono = tkinter.Tk()
    ventana_microfono.geometry("600x600")
    ventana_microfono.title("Modulo microfono")
    back_button = tkinter.Button(ventana_microfono,bg="red",fg="white",text="Atras",command=ventana2)
    back_button.place(x=4,y=4,width=50,height=30)
    etiqueta_mic = tkinter.Label(ventana_microfono,text="Capturador de voz",font=25)
    etiqueta_mic.pack(padx=4,pady=5,ipadx=4,ipady=5)

    #Contador de tiempo
    global time
    time = Label(ventana_microfono, fg='green', width=20, text="0:00:00", bg="black", font=("","30"))
    time.pack(padx=5,pady=5,ipadx=5,ipady=5)

    #BOTONES 
    btnIniciar=Button(ventana_microfono, bg="green",fg="white",width=16, text='Grabar',command=iniciar)
    btnIniciar.place(x=70,y=280,width=100,height=60)
    btnParar=Button(ventana_microfono, bg="green",fg="white", width=16, text='Parar',command=parar)
    btnParar.place(x=440,y=280,width=100,height=60)

    ventana_microfono.mainloop()
    

def file_upload():
    ventana.destroy()
    global status_microfono_archivo
    status_microfono_archivo = True
    global ventana_file
    ventana_file = tkinter.Tk()
    ventana_file.geometry("600x600")
    ventana_file.title("Modulo Carga Archivo")
    back_button = tkinter.Button(ventana_file,bg="red",fg="white",text="Atras",command=ventana2)
    back_button.place(x=4,y=4,width=50,height=30)
    etiqueta_file = tkinter.Label(ventana_file,text="Añade un archivo de audio")
    etiqueta_file.pack()
    global time
    time = Label(ventana_file,fg='green',width=20, text="Añade un archivo", bg="black", font=("","30"))
    time.pack(padx=5,pady=5,ipadx=5,ipady=5)

    archive = tkinter.Button(ventana_file, text="Examinar",bg="green",fg="white",command=lambda: modes(None))
    archive.place(x=260,y=280,width=100,height=60)

    ventana_file.mainloop()

def vistaReporte():

    global status_modo
    

    #destruir vista principal
    vistaPrinc.destroy()

    status_modo = True

    #info reporte
    global vista_reporte
    vista_reporte = tkinter.Tk()
    vista_reporte.geometry("600x600")
    vista_reporte.title("Visualizar Reporte")
    back_button = tkinter.Button(vista_reporte,bg="red",fg="white",text="Atras",command=vista_princ)
    back_button.place(x=4,y=4,width=50,height=30)

    val = getdatos(cedula)

    for i in range(len(val)):
        Input_tkinter = tkinter.Label(vista_reporte,text=str(val[i]))
        Input_tkinter.pack(padx=20,pady=7,ipadx=20,ipady=7)

    vista_reporte.mainloop()


def vista_princ():

    global cedula

    if(status_modo):
        vista_reporte.destroy()
    elif(status_modo == False):
        ventana.destroy()
    else:
        cedula = int(id_reg.get())
        vista1.destroy()


    global vistaPrinc
    vistaPrinc = tkinter.Tk()
    vistaPrinc.title("Modos")
    vistaPrinc.geometry("600x600")
    messaje_analisis=tkinter.Label(vistaPrinc,text="Bienvenido",font=25)
    messaje_analisis.pack()

    boton_gca=tkinter.Button(vistaPrinc,text="Grabar/Cargar Archivos",bg="green",fg="white",command=ventana2)
    boton_gca.place(x=70,y=280,width=140,height=60)

    boton_reporte=tkinter.Button(vistaPrinc,text="Ver reporte",bg="green",fg="white",command=vistaReporte)
    boton_reporte.place(x=440,y=280,width=140,height=60)

    vistaPrinc.mainloop()

#primer llamado
vista1 = tkinter.Tk()
vista1.title("Usuario")
vista1.geometry("600x600")
text_cedula=tkinter.Label(vista1,text="Ingrese el numero de documento")
text_cedula.pack(padx=5,pady=5,ipadx=5,ipady=5)

global id_reg

id_reg = tkinter.Entry(vista1,width=20)
id_reg.pack(padx=20,pady=7,ipadx=20,ipady=7)

boton_accept = tkinter.Button(vista1, text="Ingresar",bg="green",fg="white",command=vista_princ)
boton_accept.pack(side=tkinter.TOP)
vista1.mainloop()