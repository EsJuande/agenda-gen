# agenda-gen

Generador de agendas físicas en tamaño **A5**, pensadas para imprimir. No es una aplicación web.

Cada carilla sale como un **SVG** para abrirla y retocarla en Inkscape. Esos mismos SVG se juntan en un **PDF**, de la agenda completa o de una sección puntual.

Año: **2027**. La semana empieza el lunes.

## Herramientas

**Python 3.12+** calcula el calendario, los feriados y el orden de las carillas, y escribe cada página como SVG en tamaño A5. El texto queda como texto y los grupos con nombre, para poder corregirlos a mano en Inkscape. El PDF se arma después, a partir de esos SVG.

Python se ocupa de lo que cambia con el año: qué día cae cada fecha, cuándo un fin de semana comparte carilla, los feriados nacionales de Argentina y cuántas carillas de notas hacen falta para que el mes siguiente abra del lado derecho.

## Generar

Los comandos se corren desde la raíz del proyecto. Sirve empezar con `python` o con `python3`.

### Un mes

```
python -m agenda junio
```

```
python3 -m agenda junio
```

El mes va en minúscula, o como número del 1 al 12 (`python -m agenda 6`, `python3 -m agenda 6`).

Escribe el PDF en `output/06 - junio-2027.pdf` y una carilla SVG por archivo en `output/2027-06/`. El número del nombre es el mes, siempre con dos dígitos: `01 - enero-2027.pdf`, `09 - septiembre-2027.pdf`, `12 - diciembre-2027.pdf`.

### Primeras páginas

```
python -m agenda primeras
```

```
python3 -m agenda primeras
```

Arma datos personales, feriados, cumpleaños y el planner anual, y cierra con notas para que la portada de enero quede en página impar. El PDF queda en `output/00 - primeras-2027.pdf` y las carillas en `output/2027-primeras/`. El `00` lo deja delante de los doce meses.

### La agenda completa

No hay un comando que arme la agenda de una vez. Primero se generan las primeras páginas y después cada mes, de enero a diciembre. La portada y la contraportada todavía no las escribe el generador.

## Estructura de la agenda

1. **Portada y contraportada**
2. **Datos personales**
3. **Feriados nacionales** de Argentina
4. **Cumpleaños**
5. **Planner anual**, en dos carillas a libro abierto
6. **Los 12 meses**
   1. **Portada del mes.** Siempre del lado derecho a libro abierto.
   2. **Planner mensual.** A libro abierto, en dos carillas. Lunes, martes y miércoles a la izquierda. Jueves, viernes y el finde a la derecha: sábado y domingo comparten columna.
   3. **Días del mes.** Una carilla por día. Sábado y domingo comparten carilla: el sábado con horario de 8.00 a 14.00 y el domingo con renglones intercalados, al mismo espaciado que el resto de las hojas.
   4. **Notas**, al final del mes. Como mínimo una hoja, las dos carillas. Si con eso la portada del mes siguiente no cae en página impar, se suma una tercera carilla de notas.

### Libro abierto

En el PDF, la página impar queda a la derecha y la par a la izquierda. El margen del anillado es 16 mm y el de afuera 10 mm. En la impar el anillado queda a la izquierda. En la par, esos márgenes se invierten.

- La portada de cada mes ocupa una página impar.
- El planner mensual ocupa el pliego siguiente: lunes a miércoles en la carilla par, jueves a domingo en la impar.
- Las notas cierran el mes. Son al menos las dos carillas de una hoja. Si la página siguiente todavía no es impar, se agrega una carilla más de notas para que la portada del mes que sigue quede a la derecha.

## Salidas

Hay dos productos, y los dos salen del mismo armado de páginas:

- **SVG, una carilla por archivo.** Es el archivo de trabajo: se abre en Inkscape, se ajusta y se vuelve a exportar si hace falta.
- **PDF.** Junta las carillas ya generadas. Puede ser un mes, o las primeras páginas (datos personales, feriados, cumpleaños y planner anual).

Los SVG generados y los PDF van a `output/`. No se versionan. Las ilustraciones de origen siguen en `assets/images/`.

## Decisiones

### Feriados

Una carilla. Entran los feriados nacionales inamovibles y trasladables de la [Ley 27.399](https://servicios.infoleg.gob.ar/infolegInternet/anexos/280000-284999/281835/norma.htm). En la agenda se muestra el día en que se observan. Los trasladables —Güemes, San Martín, el Día del Respeto a la Diversidad Cultural y el Día de la Soberanía Nacional— llevan un asterisco y, al pie, la nota «Feriados trasladables». Siguen el artículo 6: martes o miércoles pasan al lunes anterior; jueves o viernes, al lunes siguiente. Si caen sábado o domingo, se quedan.

También entra el Jueves Santo. La misma ley lo fija como día no laborable y la fecha de 2027 sale de Pascua, así que es segura.

Los días no laborables con fines turísticos quedan afuera. El Poder Ejecutivo los fija cada año y, a octubre de 2026, la norma publicada ([Resolución 164/2025](https://www.boletinoficial.gob.ar/detalleAviso/primera/336753/20251226)) solo cubre 2026. Cuando salga la de 2027 se pueden sumar.

| Fecha observada | Qué es |
| --- | --- |
| vie 1 ene | Año Nuevo |
| lun 8 feb | Carnaval |
| mar 9 feb | Carnaval |
| mié 24 mar | Día Nacional de la Memoria por la Verdad y la Justicia |
| jue 25 mar | Jueves Santo, día no laborable |
| vie 26 mar | Viernes Santo |
| vie 2 abr | Día del Veterano y de los Caídos en la Guerra de Malvinas |
| sáb 1 may | Día del trabajador |
| mar 25 may | Día de la Revolución de Mayo |
| dom 20 jun | Paso a la Inmortalidad del General Manuel Belgrano |
| lun 21 jun | Güemes, trasladado del jue 17 jun |
| vie 9 jul | Día de la Independencia |
| lun 16 ago | San Martín, trasladado del mar 17 ago |
| lun 11 oct | Día del Respeto a la Diversidad Cultural, trasladado del mar 12 oct |
| sáb 20 nov | Día de la Soberanía Nacional, cae sábado y no se traslada |
| mié 8 dic | Inmaculada Concepción de María |
| sáb 25 dic | Navidad |

### Datos personales

Una carilla. El título es «datos personales», sin el año. «Esta Agenda pertenece a» con dos renglones. Después, «Contactos de emergencia»: dos contactos en la misma fila, con nombre, teléfono y correo. Alergias y medicamentos comparten la fila siguiente, con dos renglones cada uno. Al final, consideraciones especiales, con tres renglones. En las cuatro secciones, el primer renglón queda a la misma distancia del texto.

### Cumpleaños

Una carilla. Los 12 meses van en filas de tres: recuadros con el mes en tres letras y espacio en blanco debajo para anotar a mano.

### Planner anual

Dos carillas a libro abierto, leídas como filas de cuatro meses: enero y febrero a la izquierda, marzo y abril a la derecha, y así hasta noviembre y diciembre. El título es el año, solo en la carilla izquierda. Cada mes es un calendario chico. El miércoles se marca con una x y el finde va en gris.

### Carilla de día

Cada día de semana lleva el día y el mes en tres letras, el número, el signo solar del día y la fase lunar. Si ese día tiene mensajes en [`data/dias-especiales.txt`](data/dias-especiales.txt), la notificación queda centrada entre el día y el mes y el signo. Si el texto es largo, puede acercarse hasta la misma distancia que hay entre el número y el nombre del día, y no más. La estrella queda a la izquierda del texto, siempre a la misma distancia. El cuerpo de la notificación no cambia: si el texto no entra, pasa a una segunda línea, más cerrada que el interlineado que separa dos mensajes distintos. La estrella queda al medio del conjunto. Los renglones van de 8.00 a 20.00, cada media hora. La hora en punto es una línea negra continua. La media hora es gris oscuro, punteada y sin número.

Ese paso de renglón es el mismo en todas las hojas.

El boceto está en [`design/carilla-dia.svg`](design/carilla-dia.svg). El ejemplo es el miércoles 24 de marzo de 2027, con el icono de Aries y la luna llena. La tipografía de prueba es Lato.

### Carilla de finde

Sábado y domingo comparten carilla, cada uno con su encabezado. El sábado tiene horarios de 8.00 a 14.00, cada media hora, con el mismo trazo que un día de semana. El domingo no tiene horarios. Sus renglones alternan línea negra y línea gris oscuro punteada, con el mismo paso, y el bloque queda debajo del sábado.

El boceto está en [`design/carilla-finde.svg`](design/carilla-finde.svg): sábado 1 y domingo 2 de mayo de 2027. El sábado es Día del trabajador. El signo es Tauro y la luna es menguante.

### Impresión

La carilla es A5 (148,5 × 210 mm). El PDF lleva una carilla por página, en orden. La impresión es de los dos lados; el acomodo en la hoja A4 se elige en el diálogo de impresión.

El margen del anillado es 16 mm y el de afuera 10 mm. La portada, siempre impar, los lleva con el anillado a la izquierda. La carilla siguiente los invierte, y así hasta el final del mes: en cada par el anillado queda a la derecha. No hay sangrado: el contenido queda dentro de esos márgenes y no llega al corte. La tapa ocupa toda la carilla y respeta los mismos márgenes.

## Imágenes

Los SVG de los signos zodiacales están en [`assets/images/signos/`](assets/images/signos/), con nombres `zodiac-aries.svg`, `zodiac-taurus.svg` y el resto de los doce. En las carillas el trazo va incrustado: si el archivo se referencia como imagen, Inkscape lo rasteriza y el icono se ve pixelado.

Las ocho fases lunares están en [`assets/images/fases-lunares/`](assets/images/fases-lunares/). El anillo y el relleno son los del boceto. Están dibujadas para el hemisferio sur: la creciente se ilumina desde la izquierda. `muestra.svg` las junta para compararlas.

## Estado

El generador está en el paquete `agenda`. Cómo correr un mes o las primeras páginas, con `python` o con `python3`, está en [Generar](#generar). Los bocetos están en `design/`.
