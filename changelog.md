DAFI System - Registro de Cambios
=================================

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
