# Modbus Test Tool

[English version](README_EN.md)

Aplicación de escritorio escrita en Python y Tkinter para probar dispositivos Modbus. Permite leer coils y registros de forma continua, además de escribir coils y holding registers mediante conexiones TCP o serie.

<p align="center">
  <img src="testmodbus.png" alt="Modbus Test Tool" width="160">
</p>

## Características

- Conexión mediante **Modbus TCP**, **RTU sobre TCP** y **Modbus RTU**.
- Lectura continua de:
  - Coils (`01`).
  - Entradas discretas (`02`).
  - Holding registers (`03`).
  - Input registers (`04`).
- Escritura de coils y holding registers.
- Direcciones de escritura en formato decimal o hexadecimal.
- Visualización de registros en decimal, binario y número de bits activos.
- Opción para mostrar las direcciones con desplazamiento `+1`, sin modificar la consulta Modbus.
- Conversión opcional de valores a temperatura para una sonda NTC 10K 103AT-11 de AKO.
- Guardado automático de la última configuración en `config_mbus.json`.

## Requisitos

- Python 3.8 o posterior.
- Tkinter.
- Un dispositivo Modbus accesible por red o puerto serie.

> También hay ejecutables disponibles para **Linux** y **Windows**, por lo que no es necesario instalar Python ni las dependencias si utilizas una de estas versiones.

En Debian, Ubuntu y derivados, Tkinter se puede instalar con:

```bash
sudo apt install python3-tk
```

En Windows, Tkinter normalmente viene incluido con la instalación oficial de Python.

## Ejecutables para Linux y Windows

En la sección de archivos o versiones publicadas del repositorio puedes descargar el ejecutable correspondiente a tu sistema operativo:

- **Linux**: descarga el ejecutable para Linux, concédele permisos de ejecución si es necesario y ábrelo.

  ```bash
  chmod +x testmodbus
  ./testmodbus
  ```

- **Windows**: descarga el archivo `.exe` y ejecútalo directamente.

Los ejecutables incluyen las dependencias necesarias. El resto de esta documentación explica también cómo instalar y ejecutar la aplicación desde el código fuente.

## Instalación

Clona el repositorio y entra en su directorio:

```bash
git clone <URL-DEL-REPOSITORIO>
cd testModbus
```

Crea un entorno virtual e instala las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows, activa el entorno con:

```powershell
.venv\Scripts\activate
```

## Ejecución

```bash
python testmodbus1.py
```

## Uso

### 1. Configurar la conexión

Selecciona uno de los modos disponibles:

- **Modbus_TCP**: indica la dirección IP y el puerto del dispositivo. El puerto habitual es `502`.
- **RTU_OVER_TCP**: indica la IP y el puerto de la pasarela RTU/TCP.
- **Modbus_RTU**: indica el puerto serie y sus parámetros, por ejemplo `/dev/ttyUSB0` y `9600,8,N,1`. En Windows el puerto puede ser `COM3`, `COM4`, etc.

El campo **Delay** representa el tiempo máximo de espera de la comunicación, en milisegundos. **Slave** es el identificador de la unidad Modbus.

### 2. Leer datos

1. Escribe la primera dirección en **Init address**.
2. Indica en **Inc** cuántas direcciones quieres recorrer, entre 1 y 20.
3. Selecciona el tipo de dato que quieres leer.
4. Pulsa **Start** para iniciar el barrido continuo.
5. Pulsa **Stop** para detenerlo y cerrar la conexión.

La lista muestra la dirección, el tipo de lectura, el valor recibido y, para los registros, su representación binaria y el número de bits activos.

> Las direcciones usadas internamente son base 0. La opción **+1 output address** cambia únicamente la dirección mostrada en pantalla.

### 3. Escribir datos

En la sección de escritura:

1. Indica la dirección en **Address**.
2. Activa **Hex** si quieres introducirla en hexadecimal.
3. Selecciona **WRITE_COIL** o **WRITE_REGISTER**.
4. Introduce el estado del coil (`0` o `1`) o el valor del registro.
5. Pulsa **Write**.

Los valores de registro admitidos están entre `-65535` y `65535`. Antes de escribir, comprueba siempre el mapa de registros y los límites indicados por el fabricante del equipo.

## Configuración

La aplicación carga y actualiza automáticamente `config_mbus.json`. El archivo contiene valores como:

```json
{
  "ip": "192.168.1.100",
  "port": "502",
  "slave": "1",
  "inc": "20",
  "delay": "1000",
  "address": "1",
  "modbusTcp": 1,
  "com_port": "/dev/ttyUSB0",
  "baudrate": "9600,8,N,1",
  "addressPlusOne": 0,
  "hex": 0
}
```

El valor `modbusTcp` identifica el modo de conexión: `1` para Modbus TCP, `2` para RTU sobre TCP y `3` para Modbus RTU.

## Permisos del puerto serie en Linux

Si aparece un error de permisos al abrir `/dev/ttyUSB0`, añade tu usuario al grupo que controla los puertos serie (normalmente `dialout`):

```bash
sudo usermod -aG dialout "$USER"
```

Después, cierra la sesión y vuelve a entrar para aplicar el cambio.

## Aviso

La escritura de coils o registros puede cambiar el estado de una instalación real. Utiliza esta herramienta únicamente si conoces el mapa Modbus del dispositivo y puedes operar el equipo de forma segura.
