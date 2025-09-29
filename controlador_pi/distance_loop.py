import RPi.GPIO as GPIO
import time

# Constantes
doorDistance = 29.0  # Distancia del sensor a la puerta medida en centimetros
speed = 0.5            # Tiempo máximo entre detecciones para considerar que es la misma persona (Segundos)

# Pines del sensor 1
GPIO_TRIGGER_1 = 23
GPIO_ECHO_1 = 24

# Pines del sensor 2
GPIO_TRIGGER_2 = 17
GPIO_ECHO_2 = 27

# Configuración GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

def onError(sensor):
    print(f"Error con el sensor: {sensor}")

def onEvent(eventType):
    print(f"Evento detectado: {eventType}")

import time
import RPi.GPIO as GPIO

def measure_distance(trigger, echo):
    try:
        # Generar pulso en TRIG
        GPIO.output(trigger, True)
        time.sleep(0.00001)  # 10 µs
        GPIO.output(trigger, False)

        # Esperar a que ECHO suba (HIGH) con timeout
        start_time = time.time()
        timeout = start_time + 0.02  # 20 ms
        while GPIO.input(echo) == 0 and time.time() < timeout:
            start_time = time.time()
        if time.time() >= timeout:
            onError((trigger, echo))
            return None

        # Esperar a que ECHO baje (LOW) con timeout
        stop_time = time.time()
        timeout = stop_time + 0.02  # 20 ms
        while GPIO.input(echo) == 1 and time.time() < timeout:
            stop_time = time.time()
        if time.time() >= timeout:
            onError((trigger, echo))
            return None

        # Calcular distancia en cm
        elapsed = stop_time - start_time
        distance = (elapsed * 34300) / 2
        return distance

    except Exception:
        onError((trigger, echo))
        return None

try:
    while True:
        d1 = measure_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
        d2 = measure_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)

        # Guardamos si hay detección
        t = time.time()
        detected = []

        if d1 is not None and d1 < doorDistance:
            detected.append(("s1", t))
        if d2 is not None and d2 < doorDistance:
            detected.append(("s2", t))

        # Verificar secuencia de detección
        if len(detected) == 2:
            s_first, t_first = detected[0]
            s_second, t_second = detected[1]

            if (t_second - t_first) <= speed:
                if s_first == "s1" and s_second == "s2":
                    onEvent("in")
                elif s_first == "s2" and s_second == "s1":
                    onEvent("out")

except KeyboardInterrupt:
    GPIO.cleanup()
