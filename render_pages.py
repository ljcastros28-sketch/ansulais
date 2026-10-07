import fitz, os, json

CATALOGS = {
    'salas':      'ansulais_salas.pdf',
    'comedores':  'ansulais_comedores.pdf',
    'alcobas':    'ansulais_alcobas.pdf',
    'aux-salas':  'auxiliares_salas.pdf',
}
DPI     = 200   # buena calidad para tablet
QUALITY = 88

manifest = {}

for name, pdf_file in CATALOGS.items():
    if not os.path.exists(pdf_file):
        print(f'Omitiendo {name}: no se encontró {pdf_file}')
        continue

    doc   = fitz.open(pdf_file)
    total = len(doc)
    out   = os.path.join('pages', name)
    os.makedirs(out, exist_ok=True)

    r0    = doc[0].rect
    ratio = round(r0.height / r0.width, 6)
    scale = DPI / 72
    mat   = fitz.Matrix(scale, scale)

    # Renderiza páginas 2..total (página 1 = portada, manejada por SVG)
    for i in range(1, total):
        pix  = doc[i].get_pixmap(matrix=mat, alpha=False)
        path = os.path.join(out, f'p{i:02d}.jpg')
        pix.save(path, jpg_quality=QUALITY)
        print(f'{name}  {i}/{total-1}  {path}  ({os.path.getsize(path)//1024} KB)')

    doc.close()
    manifest[name] = {'count': total - 1, 'ratio': ratio}
    print(f'OK {name}: {total-1} paginas\n')

with open('manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)

print('Listo — manifest.json generado.')
print(json.dumps(manifest, indent=2))
