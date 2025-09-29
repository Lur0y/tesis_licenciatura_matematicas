import RPi.GPIO as GPIO
import time

GPIO_TRIGGER = 23
GPIO_ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def medir_distancia():
    print("\n--- Nueva medición ---")

    print("Enviando pulso en TRIG...")
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    inicio = time.time()
    timeout = inicio + 0.02
    while GPIO.input(GPIO_ECHO) == 0 and time.time() < timeout:
        inicio = time.time()
    if time.time() >= timeout:
        print("Timeout esperando que ECHO se ponga en HIGH")
        return None
    print("ECHO HIGH detectado")

    fin = time.time()
    timeout = fin + 0.02
    while GPIO.input(GPIO_ECHO) == 1 and time.time() < timeout:
        fin = time.time()
    if time.time() >= timeout:
        print("Timeout esperando que ECHO se ponga en LOW")
        return None
    print("ECHO LOW detectado")

    duracion = fin - inicio
    distancia = (duracion * 34300) / 2
    print(f"Duración: {duracion:.6f} s")
    return distancia

try:
    while True:
        dist = medir_distancia()
        if dist is not None:
            print(f"Distancia medida: {dist:.2f} cm")
        else:
            print("Medición fallida")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nMedición detenida por el usuario")
    GPIO.cleanup()

