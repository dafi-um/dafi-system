DAFI System - Registro de Cambios
=================================

## 17 Oct. 2021

* Mejorado el sistema de mensajes de sesión
* Algunos cambios y mejoras menores

## 15 Oct. 2021

### San Alberto

* Agregado panel de administración de encuestas de San Alberto

## 14 Oct. 2021

### San Alberto

* Agregado campo de ganador de encuesta
* Agregado campo para incluir una imagen de detalle en las votaciones de diseños

## 13 Oct. 2021

### San Alberto

* Actualizadas alertas de encuestas de diseños para cubrir todos los estados
* Corregidos algunos errores de diseño
* Otros cambios y mejoras menores

## 13 Oct. 2021

### Clubes

* Actualizada definición de modelos de administración

### San Alberto

* Separados modelos en distintos ficheros
* Actualizados templates
* Creado sistema de votación
* Movido CSS de templates a un fichero estático
* Renombrado `poll_index` a `poll_detail`

## 29 Sept. 2021

### Bot

* Agregada opción para iniciar `/elecciones` limpiando los delegados actuales
* Agregado comando `/mencionar` para mencionar a todos los delegados de un curso/grupo


## 27 Sept. 2021

* Varias mejoras y arreglos de errores

### Bot

* Realizado refactor
  * Eliminada la jerarquía de clases (ahora modelo funcional)
  * Eliminadas implementaciones de persistencia y programación de trabajos
* Comando `/grupos`
  * Se puede volver a solicitar en grupos y no sólo por privado
  * Se ha actualizado el formato para hacerlo más amigable
  * Se ha mejorado el rendimiento del comando
* Comandos `/vincularclub` y `/desvincularclub` eliminados
* Eliminada nuestra implementación de persistencia en favor de la de Python Telegram Bot
