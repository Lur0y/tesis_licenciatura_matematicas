import RPi.GPIO as GPIO
import time
import os
from picamera2 import Picamera2
from datetime import datetime
import cv2
import configparser

# Cargar configuración desde archivo .conf
def load_config():
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config.conf')
    config.read(config_file)
    return config

# Inicializar configuración
config = load_config()

# Constantes desde archivo de configuración
doorDistance = config.getfloat('SENSOR', 'door_distance')
speed = config.getint('SENSOR', 'speed')

# Crear directorio de fotos si no existe
photo_folder = config.get('STORAGE', 'photo_folder')
if not os.path.exists(photo_folder):
    os.makedirs(photo_folder)

# Pines del sensor 1
GPIO_TRIGGER_1 = config.getint('GPIO_PINS', 'gpio_trigger_1')
GPIO_ECHO_1 = config.getint('GPIO_PINS', 'gpio_echo_1')

# Pines del sensor 2
GPIO_TRIGGER_2 = config.getint('GPIO_PINS', 'gpio_trigger_2')
GPIO_ECHO_2 = config.getint('GPIO_PINS', 'gpio_echo_2')

# Configuración GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

# Preparacion de la camara
camera_format = config.get('CAMERA', 'format')
camera_width = config.getint('CAMERA', 'width')
camera_height = config.getint('CAMERA', 'height')
warmup_time = config.getfloat('CAMERA', 'warmup_time')
capture_frames = config.getint('CAMERA', 'capture_frames')
capture_delay = config.getfloat('CAMERA', 'capture_delay')

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": camera_format, "size": (camera_width, camera_height)}))
picam2.start()
time.sleep(warmup_time)
for _ in range(capture_frames):
    picam2.capture_array()
    time.sleep(capture_delay)

def get_next_event_id():
    """Obtiene el siguiente ID de evento desde data.txt y lo incrementa"""
    data_file = os.path.join(os.path.dirname(__file__), 'data.txt')
    
    try:
        # Leer el número actual
        with open(data_file, 'r') as f:
            content = f.read().strip()
            if content.startswith('event_number='):
                current_id = int(content.split('=')[1])
            else:
                current_id = 0
    except (FileNotFoundError, ValueError):
        # Si el archivo no existe o hay error, empezar desde 1
        current_id = 0
    
    # Incrementar para el nuevo evento
    next_id = current_id + 1
    
    # Guardar el nuevo número
    with open(data_file, 'w') as f:
        f.write(f'event_number={next_id}')
    
    return next_id

def onEvent(eventType):
    print(f"Evento detectado: {eventType}")
    print("Analizando...")
    
    # Obtener ID único para este evento
    event_id = get_next_event_id()
    print(f"ID del evento: {event_id}")
    
    # Normalizar el tipo de evento para el nombre del archivo (minúsculas, sin espacios)
    event_type_normalized = eventType.lower().replace(" ", "_")
    
    folder = config.get('STORAGE', 'photo_folder')
    photo_duration = config.getfloat('TIMING', 'photo_duration')
    photo_interval = config.getfloat('TIMING', 'photo_interval')
    
    start_time = time.time()
    contador = 1  # Empezar desde 1 para las fotos
    
    while time.time() - start_time < photo_duration:
        frame = picam2.capture_array()
        filename = f"evento_{event_id}_tipo_{event_type_normalized}_foto_no_{contador}.jpg"
        filepath = os.path.join(folder, filename)
        cv2.imwrite(filepath, frame)
        contador += 1
        time.sleep(photo_interval)
    
    print(f"Se tomaron {contador-1} fotos para el evento {event_id} (tipo: {eventType})")
    print("Esperando siguiente evento...")

import time
import RPi.GPIO as GPIO

def measure_distance(trigger, echo):
    trigger_pulse_time = config.getfloat('TIMING', 'trigger_pulse_time')
    echo_timeout = config.getfloat('TIMING', 'echo_timeout')
    
    try:
        # Generar pulso en TRIG
        GPIO.output(trigger, True)
        time.sleep(trigger_pulse_time)  # Tiempo de pulso configurable
        GPIO.output(trigger, False)

        # Esperar a que ECHO suba (HIGH) con timeout
        start_time = time.time()
        timeout = start_time + echo_timeout  # Timeout configurable
        while GPIO.input(echo) == 0 and time.time() < timeout:
            start_time = time.time()
        if time.time() >= timeout:
            return None

        # Esperar a que ECHO baje (LOW) con timeout
        stop_time = time.time()
        timeout = stop_time + echo_timeout  # Timeout configurable
        while GPIO.input(echo) == 1 and time.time() < timeout:
            stop_time = time.time()
        if time.time() >= timeout:
            return None

        # Calcular distancia en cm
        elapsed = stop_time - start_time
        distance = (elapsed * 34300) / 2
        return distance

    except Exception:
        # onError((trigger, echo))  # Comentado ya que no está definida la función
        return None

try:
    while True:
        d1 = measure_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
        d2 = measure_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)
        
        if d1 is None or d2 is None:
            continue
        
        isSomeoneInD1 = d1 < doorDistance
        isSomeoneInD2 = d2 < doorDistance
        
        if isSomeoneInD1:
            onEvent("Salida")
        if isSomeoneInD2:
            onEvent("Entrada")
    
        main_loop_delay = config.getfloat('TIMING', 'main_loop_delay')
        time.sleep(main_loop_delay)

except KeyboardInterrupt:
    GPIO.cleanup()
