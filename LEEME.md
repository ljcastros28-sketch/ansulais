# Catálogo de la tablet (almacén)

Visor a pantalla completa con las páginas de los catálogos en PDF, con el mismo estilo de ansulais.com.
Se abre `index.html` (funciona sin internet).

**Es de uso interno:** lo maneja el asesor para mostrarle los muebles al cliente. Por eso las páginas no llevan textos de venta: las de los PDF son solo la foto, y las piezas agregadas desde la web también: dos vistas lado a lado (o una sola foto centrada), sin textos. El nombre y el código de cada pieza agregada aparecen en el índice (botón de cuadritos). Todas usan el mismo marco: margen beige, foto redondeada y el logo arriba a la izquierda.

## Qué hay

| Carpeta / archivo | Qué es |
|---|---|
| `pages/<sección>/pNN.webp` | Páginas de los PDF, en tamaño para la tablet (2560 px). Las `pNN.jpg` son las originales de 4000 px: el visor ya no las usa |
| `pages/<sección>/thumbs/` | Miniaturas para el índice (botón de cuadritos) |
| `productos/<código>/` | Fotos de las piezas de la web que no están en los PDF |
| `piezas.js` | Nombre, descripción y fotos de esas piezas (lo genera el script) |
| `portadas/`, `qr/` | Foto de cada portada y código QR de cada contraportada |
| `tipografia/Montserrat-latin.woff2` | La letra de la web |

## Actualizar

- **Pieza nueva de la web:** agrégala a `PIEZAS` en `preparar_catalogo.py` (con su código de la web, por ejemplo `"SAL-40"`) y corre `python preparar_catalogo.py`.
- **PDF nuevo o actualizado:** corre `python render_pages.py` y después `python preparar_catalogo.py`, y ajusta `pages:` de esa sección en `SECCIONES` dentro de `index.html`.
- **Bifés y aparadores** (Auxiliares → Comedores) está como "próximamente": cuando haya fotos, se le pone `dir` y `pages` en `SECCIONES`, o sus piezas en `PIEZAS`.
