# Catálogo de la tablet (almacén)

Visor a pantalla completa con las páginas de los catálogos en PDF, con el mismo estilo de ansulais.com.
Dirección: **https://ljcastros28-sketch.github.io/ansulais/**

**Es de uso interno:** lo maneja el asesor para mostrarle los muebles al cliente. Por eso las páginas no llevan textos de venta: las de los PDF son solo la foto, y las piezas agregadas desde la web también: dos vistas lado a lado (o una sola foto centrada), sin textos. El nombre y el código de cada pieza agregada aparecen en el índice (botón de cuadritos). Todas usan el mismo marco: margen beige, foto redondeada y el logo arriba a la izquierda.

## Instalar en la tablet (como app)

Se instala una sola vez, con internet. Después abre a pantalla completa desde su ícono y **funciona sin internet**.

- **Tablet Android (Chrome):** abrir la dirección, esperar unos segundos y tocar el botón de descarga (flecha hacia abajo) arriba a la derecha. Si no aparece: menú ⋮ → *Instalar app* (o *Agregar a la pantalla principal*).
- **iPad (Safari):** abrir la dirección → botón Compartir → *Agregar a inicio*.

La primera vez guarda todo el catálogo (unos 26 MB). Cuando se sube una versión nueva, la app la baja sola la próxima vez que se abra con internet (si no se ve el cambio, cerrarla y abrirla otra vez).

## Qué hay

| Carpeta / archivo | Qué es |
|---|---|
| `pages/<sección>/pNN.webp` | Páginas de los PDF, en tamaño para la tablet (2560 px). Las `pNN.jpg` (4000 px) son la fuente: se quedan en el computador y no se suben |
| `pages/<sección>/thumbs/` | Miniaturas para el índice (botón de cuadritos) |
| `productos/<código>/` | Fotos de las piezas de la web que no están en los PDF |
| `piezas.js` | Código, nombre, fotos y color de fondo de esas piezas (lo genera el script) |
| `portadas/`, `qr/` | Foto de cada portada y código QR de cada contraportada |
| `app.webmanifest`, `iconos/` | Nombre, ícono y modo pantalla completa de la app |
| `sw.js` | Guarda el catálogo en la tablet para usarlo sin internet. Lo genera el script: no editarlo a mano |
| `tipografia/Montserrat-latin.woff2` | La letra de la web |

## Actualizar

**Siempre, después de cualquier cambio (también en `index.html`) y antes de subir:** correr `python preparar_catalogo.py`. Así `sw.js` cambia de versión y las tablets bajan lo nuevo.

- **Pieza nueva de la web:** agrégala a `PIEZAS` en `preparar_catalogo.py` (con su código de la web, por ejemplo `"SAL-40"`) y corre `python preparar_catalogo.py`.
- **PDF nuevo o actualizado:** corre `python render_pages.py` y después `python preparar_catalogo.py`, y ajusta `pages:` de esa sección en `SECCIONES` dentro de `index.html`.
- **Bifés y aparadores** (Auxiliares → Comedores) está como "próximamente": cuando haya fotos, se le pone `dir` y `pages` en `SECCIONES`, o sus piezas en `PIEZAS`.
