Oxobox System
==============

  Version:  2.0
  Date:     2014/08/06

Wish-List
=========
  - [ ] Formatos Manejados desde Web

Bugs
====
  
Changelog
=========

### 2014/08/05 - 2.0 - Martin - Seguimos reacomodando
* Quitamos del repositorio el Config.py.
* Seguimos con el reformateo.

### 2014/08/05 - 2.7.2.9 - Pica - Varios fixes de ids en tablas de relación, fix en js para subir desde firefox en mac
* Arreglo en el mail de asset compartido el nombre del usuario que comparte al subir por FTP

### 2014/07/30 - 2.7.2.9 - Pica - Borrado múltiple de usuarios, formatos y destinos en administración

### 2014/07/30 - 2.7.2.9 - Pica - Agregado el selector de segundos en los campos de time del standard de metadata

### 2014/07/30 - 2.7.2.9 - Pica - Opción en destino para descargar otras versiones del archivo enviado

### 2014/07/30 - 2.7.2.9 - Pica - Fix de encoding de subtítulos

### 2014/07/29 - 2.7.2.9 - Pica - Campo de Metadata con Multiplechoice

### 2014/07/28 - 2.7.2.9 - Pica - Agregadas las razones de rechazo en el destino

### 2014/07/18 - 2.7.2.9 - Martin - Wizard con help
* Creada la sección de help en el menú del perfil.
* Agregado wizard de video tips

### 2014/07/17 - 2.7.2.9 - Pica - Agregado script para servicio de soporte online

### 2014/07/16 - 2.7.2.9 - Pica - Arreglado el editor de standard de metadata

### 2014/07/16 - 2.7.2.9 - Martin - Minor Fix
* Fix en la seccion GROUP, corregido el borrar usuario.

### 2014/07/15 - 2.7.2.9 - Pica - Cambio de funcionamiento de campos de metadata obligatorio y el tamizador
* Ahora la propiedad de campo obligatorio de un Standard de Metadata se refleja solo con la tamización
* Si la configuración de tamización del grupo requiere la metadata, antes se refería a que exista
* al menos un campo, ahora significa que los campos obligatorios deben ser llenados.
* Los campos obligatorios no son obligatorios de llenar para guardarlo, tanto en los inboxes como en los assets
* Agregadito para posición de tooltips

### 2014/07/14 - 2.7.2.9 - Martin - Minor bug fixes
* Fix error al guardar perfil si no había inbox shareados con el usuario.

### 2014/07/14 - 2.7.2.9 - Pica - Minor bug fixes
* Quitado el botón de borrar un usuario compartido si el usuario no tiene permisos para hacerlo
* Player de archivos adjuntos no cargaba
* Quitado "Agregar multiple" del menú contextual de un asset aprobado
* Botón de Guardar archivos y metadata con nuevo color
* Styles fix

### 2014/07/11 - 2.7.2.9 - Pica - Nuevo mail de usuario registrado al usuario, con hardcode para DTV

### 2014/07/10 - 2.7.2.9 - Pica - Lista del dominios disponibles pasados System a Config

### 2014/07/10 - 2.7.2.9 - Pica - Fix de vista del precio en envios y SRPDF update

### 2014/07/07 - 2.7.2.9 - Pica - Administrador de uploader y compartido por inbox en administrador de grupo
* Los administradores de grupo pueden editar si un usuario es uploader o compartido en un inbox
* Desde el administrador principal se pueden editar las opciones de inbox de un usuario
* Funcionalidad para la administración de notificaciones de assets compartidos por inbox

### 2014/07/07 - 2.7.2.9 - Martin - Perfil
* Los usuarios pueden elegir de qué inbox recibe notificaciones de assets compartidos

### 2014/07/04 - 2.7.2.9 - Pica - Página de error 404

### 2014/07/04 - 2.7.2.9 - Pica - Notificación por e-mail en registro de usuario y activación

### 2014/07/03 - 2.7.2.9 - Martin - Los USERS pueden generar un excel con el listado de deliveries

### 2014/07/03 - 2.7.2.9 - Pica - Arreglado Recuperar Contraseña

### 2014/07/03 - 2.7.2.9 - Pica - Administrador de grupo, activación de usuarios, download desktop app
* Creada la sección de administración de grupo para los admin de grupos
* Opción para activar/desactivar usuarios
* Autoregistración de usuarios con subgrupos
* Autoregistración para DirecTV, con auto asignación de inboxes
* Fix de detección de tamaño de imagen de archivos
* Embed Code URL agregada para AdLatina
* Ventana de descarga de aplicación de escritorio

### 2014/06/23 - 2.7.2.9 - Pica - Usuarios autoregistrables
* Opción en grupo para habilitar el autoregistro de usuarios
* Formulario de registro de usuarios en página de grupo
* Datos extras de usuario (Company, department, position, telephone, etc)

### 2014/06/11 - 2.7.2.9 - Pica - Usuarios desactivables
* Los usuarios pueden ser desactivados para que no vuelvan a ingresar a la plataforma ni sean listados (salvo en el administrador)
* Función updateUI para JS para actualizar fácilmente un pedazo de html (usado solo en listado de users del admin)

### 2014/05/30 - 2.7.2.9 - Pica - Usuarios con permisos para finalizar y rechazar assets
* Fix de captura de tamaño de archivo de video

### 2014/03/07 - 2.7.2.9 - Pica - Fixes varios
* Captcha en login arreglado
* Orden de metadata agrupada por standard de metadata
* Indicador de archivo con vencimiento y vencido en lista de assets
* Orden de metadata
* Datos agregados al excel exportado de envíos
* Fix para reproducción de archivos con contraseña para usuarios logueados
*

### 2013/11/27 - 2.7.2.9
* Arreglos varios de envios y pagina de grupo

### 2013/10/23 - 2.7.2.9
* Listados de formatos ordenados por nombre
* Contactos de destino de childs, editables por separado de los de la cabecera
* Formatos unificados
* Fix de requerimientos de destinos
* Ubicacion remota mostrada a usuarios

### 2013/10/08 - 2.7.2.8
* Envío de mails a los responsables de destinos de tipo GROUP
* Listado de destinos child únicos de un destino GROUP cambiado
* Arreglos del mapa de georef
* Templado de pagina sin bootstrap por ahora

### 2013/09/18 - 2.7.2.7
* Georeferenciación de assets
* Vista pública de mapa
* Agregados los archivos de bootstrap para próxima implementación

### 2013/09/12 - 2.7.2.6
* Agregado de Fulltextsearch para los assets
* Fix de los requerimientos de destino. Pasó de requerir todos los formatos a al menos uno.
* Administración de envios facturados y cobrados
* Export de Deliveries en XLS, con suma de costos

### 2013/08/16 - 2.7.2.5
* Cambio de requerimientos de los destinos. Pasó de requerir TODOS los formatos seleccionados a requerir al menos uno.

### 2013/08/14 - 2.7.2.4
* Arreglo de desaparicion del buscador en pagina de asset, inhabilitando la búsqueda por tag, metadata, categoria
* DB: Cambiado e campo de groups.home_specs de TEXT a LONGTEXT
* Agregadas las opciones para habilitar o deshabilitar la página de inicio y la página de búsqueda en la página de grupo
* Agregado el sort por grupo en los envíos

### 2013/08/02 - 2.7.2.3
* Arreglado el sistema de visibilidad de las páginas de assets y de grupos
    
                            Página de asset (visibilidad)					Página de grupo
                            Público		Sin listar	Sólo grupo	Privado		Pública		Privada
Usuario del grupo
Con opt. "Solo grupo"		Si			Si			Si			No			Si			Si
Sin opt. "Solo grupo"		Si			Si			No			No			Si			Si			

Usuario invitado
Grupo con pub. de assets	Si			Si			No			No			Si			No
Grupo sin pub. de assets	No			No			No			No			Si			No

### 2013/08/01 - 2.7.2.2
* Arreglado para usuarios visualizadores con permisos de ver assets con privacidad "Solo grupo"
* Redireccionamiento automático a la página de grupo para usuarios visualizadores
* Búsqueda de grupo y usuarios por código de grupo

### 2013/07/23 - 2.7.2.1
* Tags auspiciados en página pública de grupo
    
### 2013/07/22 - 2.7.2b
* Colecciones privadas arregladas
    Arreglado el problema de las colecciones y el login para invites.
    Agregado el login para usuario.
    Las categorías públicas siempre tienen página abierta, las privadas siempre piden login o invite.
    No depende de la opción del grupo de página de grupo pública o privada.