"""
Prepara los archivos del catálogo de la tablet (se corre desde esta carpeta):

    python preparar_catalogo.py

1. Páginas: por cada pages/<seccion>/pNN.jpg (4000 px, sacadas de los PDF con
   render_pages.py) crea pNN.webp de 2560 px (lo que usa el visor) y
   thumbs/pNN.webp de 480 px (para el índice). Los .jpg no se tocan.
2. Piezas nuevas: copia desde ../web/assets/catalogo/ las fotos de las piezas que
   están en la web pero no en los PDF (lista PIEZAS de abajo) a productos/<código>/
   y escribe piezas.js con su código, nombre, fotos y color de fondo.
3. Portadas (portadas/<seccion>.webp) y códigos QR (qr/<seccion>.svg).
4. sw.js: el service worker que guarda todo el catálogo en la tablet para usarlo sin
   internet (app instalable). Lleva la lista de archivos y una versión que cambia
   cuando cambia cualquier archivo, así la tablet se actualiza sola.

Córrelo SIEMPRE después de cambiar algo (también index.html), antes de subir.

Requisitos: pip install pillow segno

Para agregar otra pieza de la web: súmala a PIEZAS con su código de la web y la
sección de la tablet donde va, y vuelve a correr el script.
"""
import hashlib
import io
import json
import os
import re
import shutil

import segno
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(AQUI, "..", "web")
os.chdir(AQUI)

# Catálogos de la web: prefijo de código -> (archivo, carpeta de fotos)
WEB_CATALOGOS = {
    "SAL": ("catalogo-salas.html", "assets/catalogo/salas"),
    "COM": ("catalogo-comedores.html", "assets/catalogo/comedores"),
    "ALC": ("catalogo-alcobas.html", "assets/catalogo/alcobas"),
    "TV": ("catalogo-muebles-tv.html", "assets/catalogo/otros/muebles-tv"),
    "MN": ("catalogo-mesas-noche.html", "assets/catalogo/otros/mesas-noche"),
    "MC": ("catalogo-mesas-centro.html", "assets/catalogo/otros/mesas-centro"),
}

# Piezas de la web que no aparecen en los PDF de la tablet (revisado página por página
# el 2026-10-06), y la sección de la tablet donde van.
PIEZAS = {
    "salas": ["SAL-36", "SAL-37", "SAL-38", "SAL-39"],
    "comedores": ["COM-25"],
    "alcobas": [],
    "aux-salas": ["TV-01", "TV-04", "TV-05", "MC-01", "MC-08", "MC-09", "MC-10", "MC-11"],
    "aux-alcobas": ["MN-%02d" % i for i in range(1, 18)],
}

# Portada de cada sección y página de la web a la que lleva el QR de la contraportada
PORTADAS = {
    "salas": ("assets/qh_salas.webp", "https://ansulais.com/catalogo-salas.html"),
    "comedores": ("assets/qh_comedores.webp", "https://ansulais.com/catalogo-comedores.html"),
    "alcobas": ("assets/qh_alcobas.webp", "https://ansulais.com/catalogo-alcobas.html"),
    "aux-salas": ("assets/qh_muebles_tv.webp", "https://ansulais.com/catalogo-otros.html"),
    "aux-alcobas": ("assets/qh_otros.webp", "https://ansulais.com/catalogo-mesas-noche.html"),
}
# Sección "próximamente" (bifés): el QR abre WhatsApp con el mensaje listo
QR_WHATSAPP = {
    "aux-comedores": "https://wa.me/573004928400?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20bif%C3%A9s%20y%20aparadores.",
}


def leer_web(prefijo):
    archivo, carpeta = WEB_CATALOGOS[prefijo]
    html = io.open(os.path.join(WEB, archivo), encoding="utf-8").read()
    filas = re.findall(r'name: "([^"]+)", desc: "[^"]*", tag: "[^"]+", folder: "([^"]+)", images: \[([^\]]*)\]', html)
    piezas = {}
    for i, (nombre, folder, imgs) in enumerate(filas):
        codigo = "%s-%02d" % (prefijo, i + 1)
        piezas[codigo] = {
            "code": codigo, "name": nombre,
            "folder": os.path.join(WEB, carpeta, folder),
            "images": re.findall(r'"([^"]+)"', imgs),
        }
    return piezas


def paginas():
    total = 0
    for seccion in sorted(os.listdir("pages")):
        carpeta = os.path.join("pages", seccion)
        os.makedirs(os.path.join(carpeta, "thumbs"), exist_ok=True)
        for f in sorted(os.listdir(carpeta)):
            if not f.endswith(".jpg"):
                continue
            base = f[:-4]
            destino = os.path.join(carpeta, base + ".webp")
            mini = os.path.join(carpeta, "thumbs", base + ".webp")
            if os.path.exists(destino) and os.path.exists(mini):
                continue
            im = Image.open(os.path.join(carpeta, f)).convert("RGB")
            grande = im.copy()
            grande.thumbnail((2560, 2560), Image.LANCZOS)
            grande.save(destino, "WEBP", quality=82, method=6)
            im.thumbnail((480, 480), Image.LANCZOS)
            im.save(mini, "WEBP", quality=72, method=6)
            total += 1
    print("páginas convertidas:", total)


def color_bordes(ruta):
    """Colores de los bordes izquierdo y derecho de la foto, de arriba a abajo (5 tramos).
    El visor los usa para pintar el fondo del marco y que la foto se funda con él."""
    im = Image.open(ruta).convert("RGB")
    w, h = im.size
    px = im.load()
    franja = max(2, w // 40)
    tramos = []
    for t in range(5):
        y0, y1 = h * t // 5, h * (t + 1) // 5
        muestras = [px[x, y] for y in range(y0, y1, 3) for x in list(range(franja)) + list(range(w - franja, w))]
        tramos.append("#%02x%02x%02x" % tuple(sum(c[i] for c in muestras) // len(muestras) for i in range(3)))
    return tramos


def piezas_nuevas():
    web = {}
    for prefijo in WEB_CATALOGOS:
        web.update(leer_web(prefijo))
    salida = {}
    for seccion, codigos in PIEZAS.items():
        salida[seccion] = []
        for codigo in codigos:
            p = web[codigo]
            carpeta = os.path.join("productos", codigo.lower())
            if os.path.isdir(carpeta):
                shutil.rmtree(carpeta)  # así no quedan fotos viejas que ya no se usan
            os.makedirs(carpeta)
            # El visor muestra la primera y la última foto lado a lado (o una sola si solo
            # hay una). La miniatura (-sm) solo hace falta de la primera, para el índice.
            usadas = p["images"][:1] + p["images"][1:][-1:]
            for k, img in enumerate(usadas):
                for suf in (("", "-sm") if k == 0 else ("",)):
                    shutil.copyfile(os.path.join(p["folder"], img + suf + ".webp"), os.path.join(carpeta, img + suf + ".webp"))
            salida[seccion].append({
                "code": p["code"],
                "name": p["name"],
                "photos": ["productos/%s/%s" % (codigo.lower(), img) for img in usadas],
                "bg": color_bordes(os.path.join(carpeta, usadas[0] + "-sm.webp")),
            })
    with io.open("piezas.js", "w", encoding="utf-8", newline="\n") as f:
        f.write("// Generado por preparar_catalogo.py: piezas de la web que no están en los PDF.\n")
        f.write("// photos: ruta sin extensión de <ruta>.webp; la primera también tiene <ruta>-sm.webp (índice).\n")
        f.write("// bg: colores del borde de la primera foto, de arriba a abajo (fondo del marco).\n")
        f.write("window.PIEZAS_NUEVAS = " + json.dumps(salida, ensure_ascii=False, indent=2) + ";\n")
    print("piezas nuevas:", {s: len(v) for s, v in salida.items()})


def portadas_y_qr():
    os.makedirs("portadas", exist_ok=True)
    os.makedirs("qr", exist_ok=True)
    qrs = {s: url for s, (_, url) in PORTADAS.items()} | QR_WHATSAPP
    for seccion, (img, _) in PORTADAS.items():
        shutil.copyfile(os.path.join(WEB, img), os.path.join("portadas", seccion + ".webp"))
    for seccion, url in qrs.items():
        segno.make(url, error="m").save(os.path.join("qr", seccion + ".svg"), scale=1, border=0, dark="#1a1a1a", light=None)
    print("portadas:", len(PORTADAS), "| QR:", len(qrs))


# Plantilla del service worker (ver service_worker())
SW = r"""// Service worker del catálogo: guarda todo el catálogo en la tablet para que funcione sin
// internet. Lo genera preparar_catalogo.py (no editarlo a mano), con la lista de
// archivos y una VERSION que cambia cuando cambia cualquier archivo; así la tablet baja
// la versión nueva sola la próxima vez que abra la app con internet.
var VERSION = '__VERSION__';
var ARCHIVOS = __ARCHIVOS__;
var CACHE = 'ansulais-catalogo-' + VERSION;

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(ARCHIVOS); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('ansulais-catalogo-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// Primero lo guardado (rápido y sin internet); si no está, de internet.
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(function (r) { return r || fetch(e.request); }));
});
"""

# Lo que la app guarda en la tablet: todo lo que usa el visor
GUARDAR = ["index.html", "piezas.js", "app.webmanifest", "favicon.ico", "favicon.svg", "apple-touch-icon.png"]
CARPETAS_GUARDAR = ["tipografia", "iconos", "portadas", "qr", "productos", "pages"]


def service_worker():
    archivos = list(GUARDAR)
    for carpeta in CARPETAS_GUARDAR:
        for raiz, _, nombres in os.walk(carpeta):
            for n in sorted(nombres):
                if n.endswith((".webp", ".svg", ".png", ".woff2")):
                    archivos.append(os.path.join(raiz, n).replace(os.sep, "/"))
    huella = hashlib.sha1()
    for a in archivos:
        huella.update(a.encode())
        with open(a, "rb") as f:
            huella.update(f.read())
    sw = SW.replace("__VERSION__", huella.hexdigest()[:10]).replace("__ARCHIVOS__", json.dumps(["./"] + archivos, indent=2))
    with io.open("sw.js", "w", encoding="utf-8", newline="\n") as f:
        f.write(sw)
    peso = sum(os.path.getsize(a) for a in archivos) / 1e6
    print("sw.js: %d archivos, %.1f MB, versión %s" % (len(archivos), peso, huella.hexdigest()[:10]))


if __name__ == "__main__":
    paginas()
    piezas_nuevas()
    portadas_y_qr()
    service_worker()
