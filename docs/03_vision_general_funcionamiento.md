[Ir al indice](index.md)
# Visión general del funcionamiento
En esta sección se explica de manera concisa el funcionamiento general del proyecto, integrando los módulos de acceso, cámaras, bitácora y servidor central.

## Acceso
La puerta permanece siempre cerrada mediante una cerradura tipo solenoide, la cual solo se abre en tres situaciones:

- Apertura remota: Cuando el administrador envía una señal específica para desbloquear la puerta.

- Apertura biométrica: Cuando una persona registrada en el sistema biométrico es reconocida.

- Falla eléctrica: La puerta se desbloquea automáticamente en caso de interrupción de la alimentación eléctrica.

Este esquema garantiza que únicamente personal autorizado tenga acceso, mientras se mantiene una vía de salida en situaciones de emergencia.

Cada vez que la puerta es manipulada (excepto en caso de falla eléctrica), se envía un JSON al servidor central con los siguientes datos:

- Fecha y hora del evento
- Identificador del cuarto de telecomunicaciones
- Tipo de evento:
    - Apertura remota 
    - Apertura por biométrico 
    - Biométrico no aceptado
- Persona que autorizó la apertura

El servidor central almacena la información en una base de datos

## Cámara
La cámara permanece siempre en funcionamiento, ya sea grabando o transmitiendo en tiempo real.

Se debe proveer acceso al streaming de datos de la cámara

## Bitácora
Cada vez que las dos "líneas" generadas por los sensores HC-SR04 son cruzadas, se ejecuta el siguiente procedimiento:

El servidor accede al streaming de la cámara y almacena imágenes durante 20 segundos.

En segundo plano, analiza las imágenes con reconocimiento facial hasta identificar a las personas presentes; si no logra identificarlas, se catalogan como "No autorizados".

El evento se etiqueta como entrada o salida, según el orden en que se crucen las líneas de los sensores.

Se envía un JSON al servidor central con los siguientes datos:

- Fecha y hora del evento.

- Identificador del cuarto de telecomunicaciones.

- Arreglo de etiquetas de identificación:

    - "No autorizado" o

    - Identificador laboral (matrícula) de la persona que ingresa o sale

    - Tipo de evento: Entrada o Salida

    - URL del servidor donde se pueden consultar las imágenes relacionadas al evento

El servidor central almacena esta información para su monitoreo y auditoría.

## Servidor central
El servidor central contiene la base de datos de bitácoras de acceso y apertura.

Proporciona dos páginas para monitoreo en tiempo real, permitiendo:

- Visualizar los eventos registrados.
- Modificar etiquetas de identificación para mejorar progresivamente el reconocimiento facial.