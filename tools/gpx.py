#!/usr/bin/env python3
"""Gera os GPX para o OsmAnd a partir dos data-*.json do site.

Correr a partir da raiz do repo:   python3 tools/gpx.py
Produz:  obidos.gpx   (Lagoa de Óbidos, detalhe todo)
         estuario.gpx (Lisboa/estuário: spots e zonas proibidas)
"""
import json, re, html, datetime, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HOJE = datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)
limpa = lambda h: re.sub(r'<[^>]+>', '', str(h)).replace('&nbsp;', ' ').strip()

def carrega(nome):
    p = RAIZ / nome
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None

def wpt(la, lo, nome, desc, tipo, cor, icone, fundo='circle'):
    return (f'<wpt lat="{la}" lon="{lo}">\n  <name>{esc(nome)}</name>\n'
            f'  <desc>{esc(desc)}</desc>\n  <type>{esc(tipo)}</type>\n'
            f'  <extensions><osmand:color>{cor}</osmand:color>'
            f'<osmand:icon>{icone}</osmand:icon>'
            f'<osmand:background>{fundo}</osmand:background></extensions>\n</wpt>')

def trk(pts, nome, desc, cor, largura='thin', fechar=True):
    seq = list(pts) + ([list(pts[0])] if fechar else [])
    seg = ''.join(f'<trkpt lat="{p[0]}" lon="{p[1]}"></trkpt>' for p in seq)
    return (f'<trk>\n  <name>{esc(nome)}</name>\n  <desc>{esc(desc)}</desc>\n'
            f'  <extensions><osmand:color>{cor}</osmand:color>'
            f'<osmand:width>{largura}</osmand:width></extensions>\n'
            f'  <trkseg>{seg}</trkseg>\n</trk>')

def grava(ficheiro, titulo, descricao, wpts, trks):
    doc = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<gpx version="1.1" creator="Pesca Barragem" '
           'xmlns="http://www.topografix.com/GPX/1/1" xmlns:osmand="https://osmand.net">\n'
           f'<metadata><name>{esc(titulo)}</name>'
           f'<desc>{esc(descricao)} | Actualizado a {HOJE} | '
           'https://j0hk3r1.github.io/Pesca-barragem/</desc>'
           f'<time>{HOJE}T00:00:00Z</time></metadata>\n'
           + '\n'.join(wpts) + '\n' + '\n'.join(trks) + '\n</gpx>\n')
    (RAIZ / ficheiro).write_text(doc, encoding='utf-8')
    print(f'{ficheiro}: {len(wpts)} pontos · {len(trks)} trilhos · {len(doc)/1024:.1f} KB')

# ---------------------------------------------------------------- Óbidos
def obidos():
    W, T = [], []
    COR = {'ok': '#27ae60', 'aviso': '#f1c40f', 'nao': '#e74c3c'}
    IC  = {'ok': 'special_marker', 'aviso': 'special_symbol_exclamation_mark',
           'nao': 'special_symbol_remove'}
    for s in carrega('data-spots-obidos.json') or []:
        nome = (f"#{s['rank']} · " if s.get('rank') else '') + re.sub(r'^[⭐⛔]\s*', '', s['n'])
        d = limpa(s['d'])
        if s.get('cast'):
            d += (f" | Lançamento {s['cast']} m para {s['rumo']}"
                  + (' COM banco de areia pelo meio' if s.get('banco') else ', sem banco pelo meio'))
        W.append(wpt(s['la'], s['lo'], nome, d, 'Spots', COR[s['v']], IC[s['v']]))
    for f in carrega('data-lancamentos.json') or []:
        curto = f['n'].split(' · ')[0]
        for u in f['rumos']:
            for D, pt in u['alvos'].items():
                if not u['principal'] and D != '60':
                    continue
                W.append(wpt(pt[0], pt[1], f"{curto} — lançar {u['rumo']} {D} m",
                             f"Alvo de lançamento. A {D} m ficas a {u['perfil'][D]} m da margem mais "
                             f"próxima. {'Rumo principal.' if u['principal'] else 'Rumo alternativo.'}",
                             'Lançamentos', '#e74c3c', 'fishing', 'square'))
            if u['principal']:
                pts = [[f['la'], f['lo']]] + [u['alvos'][d] for d in ('40', '60', '80') if d in u['alvos']]
                T.append(trk(pts, f"{curto} — linha de lançamento {u['rumo']}",
                             'Rumo principal de lançamento.', '#e74c3c', 'thick', fechar=False))
    for r in carrega('data-rampas.json') or []:
        W.append(wpt(r['la'], r['lo'], f"⛔ {r['n']} — 100 m proibidos",
                     'Edital 24/2014 da Capitania de Peniche: proibido pescar a menos de 100 m de '
                     'rampas de acesso de embarcações, embarcadouros e desembarcadouros.',
                     'Proibições', '#c0392b', 'special_symbol_remove', 'octagon'))
    CORZ = {'livre': '#27ae60', 'sazonal': '#e67e22', 'sazonal-circulo': '#e67e22',
            'condicionada-permanente': '#8e44ad', 'duvidosa': '#d35400', 'interdita': '#8b0000'}
    for z in carrega('data-lagoas.json') or []:
        if z.get('poly'):
            T.append(trk(z['poly'], z['n'], f"{limpa(z['regra'])} | {z['fonte']}",
                         CORZ.get(z['tipo'], '#8e44ad')))
    for i, p in enumerate(carrega('data-areia.json') or [], 1):
        T.append(trk(p, f'Banco de areia {i}',
                     'Fica a seco ou muito raso na baixa-mar. Não lances para aqui — passa por cima.',
                     '#f4d03f'))
    grava('obidos.gpx', 'Lagoa de Óbidos — pesca',
          'Spots por ordem, alvos de lançamento, zonas legais, rampas e bancos de areia', W, T)

# ------------------------------------------------------------- estuário
def estuario():
    W, T = [], []
    for s in re.findall(r"\['([^']+)',([\d.\-]+),([\d.\-]+),'([^']*)'\]",
                        (RAIZ / 'mapa.html').read_text(encoding='utf-8')):
        W.append(wpt(s[1], s[2], s[0], limpa(s[3]), 'Spots', '#27ae60', 'special_marker'))
    for z in carrega('data-zonas.json') or []:
        base = ('proibição NACIONAL (Portaria 14/2014, art. 8.º)' if z.get('nac')
                else 'edital da Capitania de Lisboa')
        W.append(wpt(z['la'], z['lo'], f"⛔ {z['t']} — {z['r']} m" + (f" · {z['n']}" if z.get('n') else ''),
                     f"Proibido pescar a menos de {z['r']} m. Base: {base}.",
                     'Proibições', '#c0392b', 'special_symbol_remove', 'octagon'))
    for p in carrega('data-praias.json') or []:
        W.append(wpt(p['la'], p['lo'], f"🏖️ {p['n']} — época {p['i']} a {p['f']}",
                     f"Praia balnear, capitania de {p['j']}, raio {p['r']} m. "
                     f"Na época balnear (de {p['i']} a {p['f']}) é proibido pescar entre o nascer "
                     "e o ocaso do Sol (POC-ACE, art. 17.º).",
                     'Praias', '#e67e22', 'special_sun', 'square'))
    grava('estuario.gpx', 'Lisboa e estuário — pesca',
          'Spots verificados, zonas proibidas e praias balneares', W, T)

if __name__ == '__main__':
    obidos()
    estuario()
