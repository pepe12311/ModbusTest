#!/usr/bin/env python
#  -*- coding: utf_8 -*-
"""
Programa para testear modbus José Luis Ferrer

"""
import math
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.client import ModbusTcpClient

from pymodbus.transaction import ModbusRtuFramer

    
import pymodbus.exceptions as exceptions

#from pymodbus.exceptions import ModbusIOException, ModbusError
#import numpy as np
import json
import tkinter as tk 
#from tkinter import ttk
import time
#import sys




READ_COILS=1
READ_DISCRETE_INPUTS=2
READ_HOLDING_REGISTERS=3
READ_INPUT_REGISTERS=4


root = tk.Tk()
root.title("Programa test Modbus J.L. Ferrer")
master=None
#global master


address = tk.StringVar()
slave = tk.StringVar()
ip = tk.StringVar()
iport= tk.StringVar()
inc=tk.StringVar()
delay=tk.StringVar()
contador=tk.StringVar()
contador.set("-")
estado=tk.StringVar()
estado.set("Desconectado")
werror=tk.StringVar()

baudrate=tk.StringVar()
baudrate.set("9600,8,N,1")
com_port = tk.StringVar()
com_port.set("/dev/ttyUSB0")
marcha = 0
slave_editando = False
fin_edicion_slave_id = None

texto = ["-", "READ_COILS", "READ_DISCRETE_INPUTS",
         "READ_HOLDING_REGISTERS", "READ_INPUT_REGISTERS"]

## *****calculo de temperatura con NTC de Ako, ojo solo sirve para la de AKO
checkNTC=tk.IntVar()
## para write register en dec o en hex
checkHEX=tk.IntVar()
## muestra la direccion de salida sumando 1, sin cambiar la consulta Modbus
checkAddressPlusOne=tk.IntVar()


#https://www.thinksrs.com/downloads/programs/Therm%20Calc/NTCCalibrator/NTCcalculator.htm

R = 10000      #Valor medido de R
A = 0.9059557119E-3 #¡¡¡Datos calculados NTC de Ako
B = 2.484884034E-4  
C = 2.040119886E-7  

#****************************************************************
def temp_ntc(input): 

    temp=0


    if input != 0:# para evitar division por 0   
        resistencia = R /((65536 / input) - 1)


        temp = math.log(resistencia) 
        temp = 1 / (A + (B * temp) + (C * temp * temp * temp)) 
        temp = temp - 273.15;  ## Kelvin a grados centigrados
        temp = round(temp, 5) ## redondea a 5 decimales
        temp=int(temp*10)# lo paso a entero con un decimal 20.3->203, quitarlo si se quiere un float
        #print(resistencia)

    return temp

#prueba para comprobar presion de sensor 4-20,0-10bar OJO HE renombrado NTC
def temp_ntcxxx(input): 
    bar=0
    if input != 0:# para evitar division por 0   
        ma=(input*20)/65535
        bar=(ma-4)*(10/16)

        print(bar)

    return int(bar*1000)



##***************************** INIT ************************************
def init():

    global marcha
    global master
    if marcha == 0:
        #print(marcha)
        if master:
            master.close()
        try:
            if varTcp.get() == 1:
                #master = modbus_tcp.TcpMaster(host=ip.get(),port=int(iport.get()))
                master = ModbusTcpClient(ip.get(), port=int(iport.get()),timeout=int(delay.get())/1000)
                conectado = master.connect()
                
            elif varTcp.get()==2:   
                #master = ModbusTcpClient(ip.get(), port=int(iport.get()))
                master = ModbusTcpClient(ip.get(), port=int(iport.get()), framer=ModbusRtuFramer,timeout=int(delay.get())/1000)
                #master.framer = ModbusRtuFramer
                #master.delay_ms(200)
                conectado = master.connect()
              
                #master = modbus_rtu_over_tcp.RtuOverTcpMaster(host=ip.get(),port=int(iport.get()))
            else:
                s=baudrate.get()
                s=s.replace(" ", "")# quito espacios
                s=s.split(",")# cojo datos separados por comas
                #master = modbus_rtu.RtuMaster(serial.Serial(port=com_port.get(),  baudrate=int(s[0]), bytesize=int(s[1]), parity=s[2], stopbits=int(s[3]), xonxoff=0))
                master = ModbusClient(method='rtu', port=com_port.get(), baudrate=int(s[0]), bytesize=int(s[1]), parity=s[2], stopbits=int(s[3]),timeout=int(delay.get())/1000)
                
                conectado = master.connect()
         
                
            #master.set_timeout(1)
            #logger = modbus_tk.utils.create_logger("console")
            #logger.info("connected")
            
    
            if not conectado:
                raise exceptions.ConnectionException("No se pudo establecer la conexión Modbus")

        except Exception as e:
            marcha = 0
            estado.set("Error de conexion")
            werror.set("Error de conexión: " + str(e))
            print("Se ha producido una excepción de conexión:", e)
            if master:
                master.close()
            return False

        marcha = 1
        estado.set("Conectado")
        return True

    return True

#*******************************************************************

def putConfig():
    config = {"ip": "192.168.1.100", "port": "502","slave": "1","inc": "20", "delay": "1000", "address": "1", "modbusTcp" :1, "com_port": "/dev/ttyUSB0", 
             "baudrate": "9600,8,N,1"}
 
    config["ip"] = ip.get()
    config["port"] = iport.get()
    config["inc"] = inc.get()
    config["delay"] = delay.get()
    config["com_port"] = com_port.get()
    config["baudrate"] = baudrate.get()
    config["slave"] = slave.get()
    config["address"] = address.get()
    config["modbusTcp"] = varTcp.get()

    with open('config_mbus.json', 'w') as f:
        json.dump(config, f)
    #print(config)

#*******************************************************************

def getConfig():
    defaults = {"ip": "192.168.1.100", "port": "502", "slave": "1",
                "inc": "20", "delay": "1000", "address": "1",
                "modbusTcp": 1, "com_port": "/dev/ttyUSB0",
                "baudrate": "9600,8,N,1"}

    try:
        with open('config_mbus.json', 'r') as f:
            config = json.load(f)
        if not isinstance(config, dict):
            raise ValueError("La configuración no es un objeto JSON")
        config = {**defaults, **config}
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        config = defaults.copy()
        with open('config_mbus.json', 'w') as f:
            json.dump(config, f)

    ip.set(config["ip"])
    iport.set(config["port"])
    inc.set(config["inc"])
    delay.set(config["delay"])
    com_port.set(config["com_port"])
    baudrate.set(config["baudrate"])
    slave.set(config["slave"])
    address.set(config["address"])
    varTcp.set(config["modbusTcp"])

    return config
  
     
    


#********************************************************************
def start():
    global marcha
    #global master
    print("start")
    if marcha:
        return

    werror.set("")
    putConfig()
    if init():
        bOn.configure(state=tk.DISABLED)
        try:
            ejecuta()
        finally:
            bOn.configure(state=tk.NORMAL)
       
        

#*******************************************************************
def stop():
    print("stop")
    global marcha
    global master
    marcha = 0
    estado.set("Desconectado")
    #print(master)
    #if master:
    if master:
        master.close()
    putConfig()
    bWrite.configure(state = tk.NORMAL)
    bOn.configure(state = tk.NORMAL)
    
  
#*********************************************************************
#Para que al cerrar la ventana primero cierre la conexión
def salir():
    stop()
    root.destroy()  

root.protocol("WM_DELETE_WINDOW", salir)



#*******************************************************************
def sel1():
    selection = "You selected the option " + str(var1.get())
    # tk.Label.config(text = selection)
    eBaudios.configure(state = tk.DISABLED)
    eComPort.configure(state = tk.DISABLED)
    eIp.configure(state = tk.NORMAL)
    ePort.configure(state = tk.NORMAL)
        
def sel2():
    selection = "You selected the option " + str(var1.get())
    # tk.Label.config(text = selection)
    eIp.configure(state = tk.DISABLED)
    ePort.configure(state = tk.DISABLED)
    eBaudios.configure(state = tk.NORMAL)
    eComPort.configure(state = tk.NORMAL)
        

#*******************************************************************
def incrementa():
    try:
        n=int(inc.get())
        s = int(address.get())
    except ValueError:
        return
    s += n
    address.set(str(s))


#*******************************************************************
def decrementa():
    try:
        n=int(inc.get())
        s = int(address.get())
    except ValueError:
        return
    s -= n
    if s < 0:
        s = 0
    address.set(str(s))

#*******************************************************************

#*******************************************************************
def wInc_dec(modo, valor, hexadecimal=False):
    base = 16 if hexadecimal else 10
    texto = valor.get().strip()
    if texto.lower() == "0x":
        texto = ""
    n = int(texto, base) if texto else 0
    if modo=="+":
        n+=1
    else:
        if n>0: n-=1

    valor.set(format(n, "X") if hexadecimal else str(n))


def cambia_formato_address():
    """Convierte el contenido de Address al marcar o desmarcar Hex."""
    texto = wAddress.get().strip()
    if not texto or texto.lower() == "0x":
        wAddress.set("0")
        return

    try:
        if checkHEX.get() == 1:
            numero = int(texto, 10)
            wAddress.set(format(numero, "X"))
        else:
            numero = int(texto, 16)
            wAddress.set(str(numero))
    except ValueError:
        werror.set("Direccion no valida")


#*******************************************************************
def signed16(n):
    s16 = (n + 2**15) % 2**16 - 2**15
    return s16



#*******************************************************************

def inicio():
    getConfig()  
    if varTcp.get() < 3:
        sel1()
    else:    
        sel2()

#*******************************************************************
def set01(v):
    if v.get()==0:
        v.set(1)
        bt01.configure(fg="red",bg="yellow")
    else:
        v.set(0)
        bt01.configure(fg="black",bg="lightgray")
  
#*********************** WRITE COIL/REGISTER ********************************************

def write_register(coil_or_register, address,register,bit):
    global marcha
    global master

    estaba_leyendo = marcha == 1
    bWrite.configure(state=tk.DISABLED)
    werror.set("")

    try:
        # Si no hay una lectura activa, abre una conexión solo para escribir.
        # Durante el bucle se reutiliza la conexión existente: Tkinter ya ha
        # pausado la lectura mientras ejecuta este callback.
        if not estaba_leyendo:
            if not init():
                raise exceptions.ConnectionException("No se pudo abrir la conexión Modbus")

        registro=int(register.get())
        if registro < -65535 or registro > 65535:
            raise ValueError("El registro debe estar entre -65535 y 65535")
        if registro <0: #si el número es negativo lo convierto para poder mandarlo por modbus
            registro=65536+registro

        address_base = 16 if checkHEX.get() == 1 else 10
        write_address = int(address.get(), address_base)
        if write_address < 0 or write_address > 65535:
            raise ValueError("La dirección debe estar entre 0 y 65535")

        if  coil_or_register.get()==1:
        
            result=master.write_register(write_address, registro, int(slave.get()))
            #result=master.write_register( int(address.get()),65536-16, int(slave.get()))
            
            
            #read_result = master.read_holding_registers(address=100, count=1)
            
        else:
        
            result=master.write_coil(write_address, bit.get(), int(slave.get()))    
        
    except  Exception as e:
        print(e)    
        ss=e
    else:
        ss=result
    finally:
        # Una escritura independiente no debe dejar el programa en marcha.
        if not estaba_leyendo:
            stop()
        bWrite.configure(state=tk.NORMAL)

    ss=str(ss)
    ss=ss.replace("Modbus Error:","")
    werror.set(ss)
    
            
        
     
    
   
#*********************************************************************   

def test_is_digit(input):# para testear entrada tk.Entry.
      
    if input.lstrip("-").isdigit(): #acepta números negativos
        #print(input) 
        return True
                          
    elif input =="": 
        #print(input) 
        return True
    elif input =="-": 
        #print(input) 
        return True
  
    else: 
        #print(input) 
        return False


def test_address(input):
    """Valida la direccion de escritura como decimal o hexadecimal."""
    if input == "":
        return True

    if checkHEX.get() == 1:
        value = input[2:] if input.lower().startswith("0x") else input
        return value == "" or all(char in "0123456789abcdefABCDEF" for char in value)

    return input.isdigit()


def inicia_edicion_slave(event=None):
    """Pausa el barrido mientras se modifica el numero de Slave."""
    global slave_editando
    slave_editando = True
    estado.set("Editando Slave")


def termina_edicion_slave(event=None):
    """Permite reanudar el barrido cuando termina la edicion."""
    global slave_editando, fin_edicion_slave_id
    if fin_edicion_slave_id is not None:
        root.after_cancel(fin_edicion_slave_id)
        fin_edicion_slave_id = None
    slave_editando = False
    if event is not None and getattr(event, "keysym", None) == "Return":
        root.focus_set()


def confirma_slave_tras_pausa():
    """Aplica automaticamente el Slave tras una pausa al escribir."""
    global fin_edicion_slave_id
    fin_edicion_slave_id = None
    termina_edicion_slave()


def programa_fin_edicion_slave(event=None):
    """Reinicia el tiempo de espera cada vez que cambia el campo."""
    global slave_editando, fin_edicion_slave_id
    slave_editando = True
    estado.set("Editando Slave")
    if fin_edicion_slave_id is not None:
        root.after_cancel(fin_edicion_slave_id)
    fin_edicion_slave_id = root.after(700, confirma_slave_tras_pausa)
 

#************ REGISTRA TEST_IS_DIGIT PARA LOS tk.Entry*******

reg = root.register(test_is_digit)
regAddress = root.register(test_address)

#************************CREACION DE VENTANA********************************************

frame = tk.Frame(root, height=100, width=400, relief=tk.SUNKEN, bd=2)
frame.grid(row=0, column=0, sticky=tk.W + tk.E)

frame0 = tk.Frame(root, height=100, width=400, relief=tk.SUNKEN, bd=2)
frame0.grid(row=1, column=0, sticky=tk.W + tk.E)

frame1 = tk.Frame(root, relief=tk.SUNKEN, bd=1)
frame1.grid(row=2, column=0, sticky=tk.W + tk.E)



##******** WRITE REGISTERS *************

wAddress=tk.StringVar(value="0")
register = tk.StringVar()

frame2 = tk.Frame(root, relief=tk.SUNKEN, bd=1)
frame2.grid(row=3, column=0, sticky=tk.W + tk.E)

frame3 = tk.Frame(root, relief=tk.SUNKEN, bd=1,bg="white")
frame3.grid(row=4, column=0, sticky=tk.W + tk.E)

labelAddress = tk.Label(frame2, text="Address")
labelAddress.grid(row=0, column=0, sticky=tk.E)

eWriteAdress= tk.Entry(frame2, background='white', textvariable=wAddress,width=8,validate ="key", validatecommand =(regAddress, '%P'))
eWriteAdress.grid(column=1, row=0,sticky=tk.W)

## Decimal o Hexadecimal******************************************************************

checkBHex=tk.Checkbutton(frame2, text="Hex", fg ="blue", variable=checkHEX, onvalue=1, offvalue=0,
                         command=cambia_formato_address)
checkBHex.grid(column=2, row=0, sticky=tk.W)

##*****************************************************************************************


# incrementa o decrementa el registro a escribir
wbMenos = tk.Button(frame2, text=" - ", command=lambda: wInc_dec("-",wAddress,checkHEX.get()==1))
wbMas = tk.Button(frame2, text=" + ", command=lambda: wInc_dec("+",wAddress,checkHEX.get()==1))

wbMenos.grid(column=3, row=0, sticky=tk.E)
wbMas.grid(column=4, row=0, sticky=tk.E)

##***********Radio tk.Button  coil or register 

coil_or_register=tk.IntVar()

rbCoil =     tk.Radiobutton(frame2, text="WRITE_COIL --->", fg="GREEN",variable=coil_or_register,value=0)
rbRegister = tk.Radiobutton(frame2, text="WRITE_REGISTER",fg="green",variable=coil_or_register,value=1)
rbCoil.grid(column=0, row=1, sticky=tk.W)
rbRegister.grid(column=0, row=2, sticky=tk.W)

rbCoil.select()

#werror=tk.StringVar()
labelErrorW = tk.Label(frame3, textvariable=werror,bg="yellow")
labelErrorW.grid(column=0,row=0, sticky="ew")
#labelErrorW.pack(fill=ttk.X)
#labelErrorW.place(relx=0.5, rely=0.5)
frame3.columnconfigure(0, weight=1)



##********** 0 o 1 ********************
v00=tk.IntVar()
v00.set(0)

##**********boton de 0 o 1 ********
bt01= tk.Button(frame2, anchor=tk.W,textvariable=str(v00), command= lambda: set01(v00))
bt01.grid(column=1, row=1, sticky=tk.W)


#**********entrada register****

register.set("0")
eRegister = tk.Entry(frame2, background='white', textvariable=register,width=8)
eRegister.grid(column=1,row=2, sticky=tk.W)

eRegister.config(validate ="key", validatecommand =(reg, '%P'))#comprueba que es un número

## Llama a la función write_register.....register es Strinvar

bWrite = tk.Button(frame2, text="Write", command=lambda: write_register(coil_or_register, wAddress, register,v00))
bWrite.grid(column=10, row=2, sticky=tk.E)


##***************************************************************************************************************


    
#text = tk.
# StringVar(value="Output")
#text.set("Output")

labelIp = tk.Label(frame0, text="IP")
labelPort = tk.Label(frame0, text="Port")
labelIa = tk.Label(frame, text="Init address", anchor=tk.W)
labelInc = tk.Label(frame, text="Inc", anchor=tk.W)
labelDelay = tk.Label(frame, text="Delay", anchor=tk.W)
labelMillisecons = tk.Label(frame, text="Millisecons", anchor=tk.W)
labelSlave = tk.Label(frame, text="Slave", fg="blue",anchor=tk.W)
labelCom = tk.Label(frame0, text="(9600,8,N,1) [N or E]", anchor=tk.W)

labelIp.grid(row=0, column=1, sticky=tk.W)
labelPort.grid(row=0, column=3, sticky=tk.W)
labelIa.grid(row=1, column=0, sticky=tk.W)
labelInc.grid(row=1, column=4, sticky=tk.E)
labelDelay.grid(row=1, column=6, sticky=tk.E)
labelMillisecons.grid(row=1, column=8, sticky=tk.E)
labelSlave.grid(row=2, column=0, sticky=tk.W)
labelCom.grid(row=2, column=4, sticky=tk.W)


#  label4.grid(row=0,column=3)


eIp = tk.Entry(frame0, background='white', textvariable=ip)

ePort = tk.Entry(frame0, background='white', textvariable=iport,width=6,validate ="key", validatecommand =(reg, '%P'))
eAdress = tk.Entry(frame, background='white', textvariable=address,width=6,validate ="key", validatecommand =(reg, '%P'))
eInc = tk.Entry(frame, background='white', textvariable=inc,width=6,validate ="key", validatecommand =(reg, '%P'))
eDelay = tk.Entry(frame, background='white', textvariable=delay,width=6,validate ="key", validatecommand =(reg, '%P'))
eSlave = tk.Entry(frame, background='white', textvariable=slave,width=6,bg="lightblue"  ,validate ="key", validatecommand =(reg, '%P'))
eSlave.bind("<FocusIn>", inicia_edicion_slave)
eSlave.bind("<KeyRelease>", programa_fin_edicion_slave)
eSlave.bind("<FocusOut>", termina_edicion_slave)
eSlave.bind("<Return>", termina_edicion_slave)


##eInc.config(validate ="key",   validatecommand =(reg, '% P')) # para testear entrada tk.Entry...no está activo 
# e4 = tk.Entry(tk.Frame,background='white',textvariable=count)

eIp.grid(row=0, column=2, padx=5)
ePort.grid(row=0, column=3, padx=5)
eAdress.grid(row=1, column=1, padx=5,sticky=tk.W)
eInc.grid(row=1, column=5, padx=5,sticky=tk.W)
eDelay.grid(row=1, column=7, padx=5,sticky=tk.W)
eSlave.grid(row=2, column=1, padx=5,sticky=tk.W)

checkAddressPlusOneButton = tk.Checkbutton(
    frame,
    text="+1 output address",
    fg="blue",
    variable=checkAddressPlusOne,
    onvalue=1,
    offvalue=0
)
checkAddressPlusOneButton.grid(row=2, column=2, sticky=tk.W)





##----------------------------------------------------------
varTcp = tk.IntVar() ## tcp o modbus_tcp
rbTcp = tk.Radiobutton(frame0, text="Modbus_TCP",
                  fg="blue", variable=varTcp, value=1, command=sel1)
rbRtuTcp = tk.Radiobutton(frame0, text="RTU_OVER_TCP",
                  fg="blue", variable=varTcp, value=2, command=sel1)
rbRtu = tk.Radiobutton(frame0, text="Modbus_RTU",
                  fg="blue", variable=varTcp, value=3, command=sel2)

eBaudios = tk.Entry(frame0, background='white', textvariable=baudrate,width=12) ## "9600,8,N,1"
eComPort = tk.Entry(frame0, background='white', textvariable=com_port,width=14)

rbTcp.select()

rbTcp.grid(column=0, row=0, sticky=tk.W)
rbRtuTcp.grid(column=0, row=1, sticky=tk.W)
rbRtu.grid(column=0, row=2, sticky=tk.W)
eSlave.grid(column=1,row=2, padx=5,sticky=tk.W)

eComPort.grid(column=2,row=2, padx=5,sticky=tk.W)
eBaudios.grid(column=3,row=2, padx=5,sticky=tk.W)

#separador= Tk.Separator(frame1,orient="horizontal")
#separador.place(relx=0, rely=0.36, relwidth=1, relheight=1)


var1 = tk.IntVar() # tipo de entrada 1,2,3,4
rb1 = tk.Radiobutton(frame1, text="1-READ_COILS-R/W", fg="red",
                  variable=var1, value=1)
rb2 = tk.Radiobutton(frame1, text="2-READ_DISCRETE_INPUTS-R",
                  fg="red", variable=var1, value=2)
rb3 = tk.Radiobutton(frame1, text="3-READ_HOLDING_REGISTERS-R/W",
                  fg="red", variable=var1, value=3)
rb4 = tk.Radiobutton(frame1, text="4-READ_INPUT_REGISTERS-R",
                  fg="red", variable=var1, value=4)
rb3.select()

rb1.grid(column=0, row=3, sticky=tk.W)
rb2.grid(column=0, row=4, sticky=tk.W)
rb3.grid(column=0, row=5, sticky=tk.W)
rb4.grid(column=0, row=6, sticky=tk.W)



#labelNTC = tk.Label(frame1, text="NTC-10k")
#labelNTC.grid(column=3, row=6, sticky=tk.W + tk.E)

checkB1=tk.Checkbutton(frame1, text="Value->NTC10K-103AT-11(AKO)", fg ="blue", variable=checkNTC, onvalue=1, offvalue=0)
checkB1.grid(column=3, row=6, sticky=tk.W + tk.W)

error = tk.StringVar()
error.set("----")
#labelError = tk.Label(frame1, textvariable=error, relief=tk.SUNKEN,fg="red", bd=1, width=30)
#labelError.grid(column=3, row=6, sticky=tk.W + E)

#frame2 = tk.Frame(root, height=100, width=100, relief=tk.SUNKEN, bd=1,bg="red")


#  frame2.grid(row=1,column=2,sticky=tk.E,padx=5)

bMas = tk.Button(frame, text=" - ", command=lambda: decrementa())
bMenos = tk.Button(frame, text=" + ", command=lambda: incrementa())

bOn = tk.Button(frame, text="Start", command=start)
bStop = tk.Button(frame, text="Stop", command=stop)

bMas.grid(column=2, row=1, sticky=tk.E)
bMenos.grid(column=3, row=1, sticky=tk.E)

#bMas.place(relx = .5, rely =.5, anchor = NE)
#bMenos.place(relx)


#bOn.grid(column=9, row=0, sticky=N)
#bStop.grid(column=11, row=0, sticky=N)
bOn.place(relx = 0.915, anchor = tk.NE)
bStop.place(relx = 1, anchor = tk.NE)

# image.grid(row=0, column=2, columnspan=2, rowspan=2,sticky=tk.W+E+N+S, padx=5, pady=5)

varListbox = tk.StringVar()
listbox = tk.Listbox(root, width=80, height=21,bg="light cyan",  bd=5, relief=tk.SUNKEN, font="TkFixedFont")
listbox.grid(column=0, row=7, padx=20, pady=20)

# Barra de estado al pie de la ventana.
footer = tk.Frame(root, relief=tk.SUNKEN, bd=1)
footer.grid(column=0, row=8, sticky=tk.W + tk.E)
footer.columnconfigure(1, weight=1)

tk.Label(footer, text="Estado:", anchor=tk.W).grid(column=0, row=0, padx=(6, 3), pady=2)
labelEstado = tk.Label(footer, textvariable=estado, anchor=tk.W)
labelEstado.grid(column=1, row=0, sticky=tk.W, pady=2)

tk.Label(footer, text="Contador:", anchor=tk.E).grid(column=2, row=0, padx=(6, 3), pady=2)
labelContador = tk.Label(footer, textvariable=contador, width=8, relief=tk.SUNKEN, bd=1, anchor=tk.E)
labelContador.grid(column=3, row=0, padx=(0, 6), pady=2)

root.columnconfigure(0, weight=1)


#*******************************************************************
def ejecuta():
    #slaveH=0
    #text = tk.StringVar(value="Output")
    global marcha
    t = 0
    listbox.delete(0,tk.END)
    
    while (marcha):    
        i=0

        if slave_editando:
            estado.set("Editando Slave")
            root.update()
            root.after(50)
            continue
       
        try:
            addr = int(address.get())
        except ValueError:
            addr = 0
            address.set(str(addr))
        if addr < 0 or addr > 65535:
            addr = min(max(addr, 0), 65535)
            address.set(str(addr))
        read_type = var1.get()

        # El usuario puede dejar el campo vacio unos instantes mientras edita.
        # En ese caso se pausa la lectura hasta que haya un Slave valido.
        try:
            slave_actual = int(slave.get())
            if slave_actual < 0 or slave_actual > 247:
                raise ValueError
        except ValueError:
            estado.set("Esperando Slave valido")
            root.update()
            root.after(50)
            continue
        
        
        try:
            incremento=int(inc.get())
        except ValueError:
            incremento=20
            inc.set(str(incremento))
        if incremento <1 or incremento >20:
            incremento=20
            inc.set(str(incremento))
            
        # if slave.get().find('h') or slave.get().find('H'):
        #     #print(int(slaveH))
        #     slaveH=hex(slave.get())
        # else:
        #     slaveH=int(slave.get())
                        
        for n in range(addr, min(addr + incremento, 65536)):
            ###time.sleep(.1)
            output_address = n + checkAddressPlusOne.get()
            
            try:
                if read_type == READ_COILS:
                    read=master.read_coils(address=n, count=1,slave=slave_actual)
                elif read_type == READ_DISCRETE_INPUTS:
                    read=master.read_discrete_inputs(address=n, count=1,slave=slave_actual)
                elif read_type == READ_HOLDING_REGISTERS:
                     read=master.read_holding_registers(address=n, count=1,slave=slave_actual)
                elif read_type == READ_INPUT_REGISTERS:
                   read=master.read_input_registers(address=n, count=1,slave=slave_actual)
                    
                    
                ##resistencia = (1107 * r2)/(65536-r2)
                ######resistencia = 1100*((65536.0 / r2) - 1)
                #print(resistencia)
                
                if not read.isError():
                    error.set("OK")
                    estado.set("Conectado")

                    bit_count = 0
                    color="light cyan"
                    if read_type == READ_COILS or read_type == READ_DISCRETE_INPUTS:
             
                        r1=read.bits[0]
       
                        s= f"{output_address:<5} {texto[read_type]:10s}  {int(r1)} [{r1}]"  
                          
                    else:
                        r1=int(read.registers[0])
                        if checkNTC.get()==1:
                            r1=temp_ntc(r1)
                    
                        #print(temp)
                        bit_count=int.bit_count(r1)
                        
            
                        binary = f"{r1:0>16b}"
                    
                        s= f"{output_address:<5} {texto[read_type]:10s} {r1:8} [{binary}] {bit_count}"    
              
                else:
                   # print(read)

                    estado.set("Error Modbus")
                    s=f"{output_address} {read}"
                    color="yellow"
                   
                   # s=s.replace("Modbus Error:","")
                   # s=s.replace("[Input/Output]","")
                   # error.set(s)
                    print(s)
             
            # Manejar la excepción de conexión aquí, por ejemplo, intentar reconectar
            #except pymodbus.exceptions.ConnectionException as e:
             
            except Exception as e:
                #print(master)
                print("Se ha producido una excepción de conexión:", e)
                
                #marcha=False               
                error.set(str(e))
                estado.set("Error de comunicacion")
                s=e
                color="yellow"
                print(e)
                if "ModbusSerialClient" in str(e):
                    time.sleep(1)
             
            
            
            listbox.delete(i)
            s=str(s)
            s=s.replace("Modbus Error:","")
            s=s.replace("[Input/Output]","")
            listbox.insert(i,s)    
            listbox.itemconfig(i,{'bg':color})        
           
            i=i+1
            #print(s)
            contador.set("{: >5}".format(str(output_address)))
            #  root.update_idletasks()
          

            root.update()# es imprescindible
            if marcha==0 or slave_editando:
                break

        # Pequeña pausa entre barridos para no saturar el dispositivo ni la CPU.
        if marcha:
            root.after(10)
   
            #print(n, error.get())



 

inicio()
 
root.mainloop()
