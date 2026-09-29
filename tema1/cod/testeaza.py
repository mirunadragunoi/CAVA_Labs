"""
verificari pentru Task 1

    python testeaza.py              # toate verificarile
    python testeaza.py --scurt      # doar rezumatul
    python testeaza.py --jocuri 1 2 # doar anumite jocuri de antrenare

rulez patru verificari, in ordinea in care se strica lucrurile in practica:

  1. detectia tablei - daca grila nu e gasita corect, tot restul e inutil
  2. acuratetea pe antrenare - acolo unde am adnotari
  3. acuratetea pe fake_test - un joc pe care nu l-am folosit deloc la reglaje
  4. marja de incredere - cat de aproape a fost a doua celula clasata

a patra e cea mai utila dintre toate: imi arata mutarile care au iesit corecte
"din intamplare", cu marja mica. Alea sunt cele care se vor strica pe alt joc.
"""

import os
import glob
import argparse

import numpy as np
import cv2 as cv

import config
from tabla import indreapta_tabla, detecteaza_colturi, deseneaza_grila, pozitie_la_index
from task1 import (imagini_joc, scoruri_schimbare, gaseste_piesa_noua, incredere, proceseaza_joc)
from evalueaza import citeste_pozitie


DIR_DEPANARE = os.path.join(config.DIR_REZULTATE, 'depanare')


# 1. detectia tablei
def verifica_detectia_tablei(cai, verbose=True):
    """tabla e fotografiata din aceeasi pozitie fixa, deci colturile gasite
    ar trebui sa fie aproape identice de la o imagine la alta. Daca una iese
    din rand, acolo s-a stricat detectia si merita sa ma uit la ea."""

    print('\n[1] DETECTIA TABLEI (%d imagini)' % len(cai))

    dimensiuni = []
    suspecte = []

    for cale in cai:
        img = cv.imread(cale)
        if img is None:
            suspecte.append((os.path.basename(cale), 'nu se poate citi'))
            continue
        try:
            c = detecteaza_colturi(img)
        except ValueError as e:
            suspecte.append((os.path.basename(cale), str(e)))
            continue

        lat = np.linalg.norm(c[1] - c[0])
        inalt = np.linalg.norm(c[3] - c[0])
        dimensiuni.append((os.path.basename(cale), lat, inalt, c[0][0], c[0][1]))

    if not dimensiuni:
        print('   nicio imagine procesata')
        return suspecte

    d = np.array([[x[1], x[2], x[3], x[4]] for x in dimensiuni])
    print('   latime : %.0f .. %.0f pixeli' % (d[:, 0].min(), d[:, 0].max()))
    print('   inaltime: %.0f .. %.0f pixeli' % (d[:, 1].min(), d[:, 1].max()))
    print('   coltul stanga-sus: x %.0f..%.0f   y %.0f..%.0f'
          % (d[:, 2].min(), d[:, 2].max(), d[:, 3].min(), d[:, 3].max()))

    raport = d[:, 0] / d[:, 1]
    print('   raport latime/inaltime: %.3f .. %.3f (ar trebui sa fie ~1.0, grila e patrata)'
          % (raport.min(), raport.max()))

    # semnalez imaginile care se abat mult de la mediana
    mediana = np.median(d[:, :2], axis=0)
    for nume, lat, inalt, _, _ in dimensiuni:
        if abs(lat - mediana[0]) > 0.05 * mediana[0] or abs(inalt - mediana[1]) > 0.05 * mediana[1]:
            suspecte.append((nume, 'dimensiuni neobisnuite: %.0f x %.0f' % (lat, inalt)))

    if suspecte:
        print('   ATENTIE, imagini suspecte:')
        for nume, motiv in suspecte:
            print('      %s: %s' % (nume, motiv))
    else:
        print('   toate imaginile dau aceeasi grila -> detectia e stabila')

    return suspecte


# 2 + 3. acuratetea, cu marje
def ruleaza_cu_marje(director_imagini, joc, director_adnotari, eticheta='', verbose=True):
    """Ca proceseaza_joc, dar retine si marja de incredere si compara pe loc
    cu adnotarea, ca sa pot analiza greselile."""
    cai = imagini_joc(director_imagini, joc)
    if not cai:
        return None

    tabla_goala = cv.imread(config.IMAGINE_TABLA_GOALA)
    tabla_inainte = indreapta_tabla(tabla_goala)

    ocupate = set()
    randuri = []

    for cale in cai:
        nume = os.path.splitext(os.path.basename(cale))[0]
        tabla_acum = indreapta_tabla(cv.imread(cale))
        i, j, scoruri = gaseste_piesa_noua(tabla_acum, tabla_inainte, ocupate)

        pozitie = '%d%s' % (i + 1, chr(ord('A') + j))
        marja = incredere(scoruri, ocupate)

        adevar = None
        cale_gt = os.path.join(director_adnotari, nume + '.txt')
        if os.path.exists(cale_gt):
            adevar = citeste_pozitie(cale_gt)

        randuri.append({'nume': nume, 'cale': cale, 'pozitie': pozitie,
                        'adevar': adevar, 'marja': marja, 'ij': (i, j),
                        'tabla': tabla_acum, 'set': eticheta or 'necunoscut'})

        ocupate.add((i, j))
        tabla_inainte = tabla_acum

    return randuri


def raport_joc(randuri, eticheta, verbose=True):
    cu_adevar = [r for r in randuri if r['adevar'] is not None]
    gresite = [r for r in cu_adevar if r['pozitie'] != r['adevar']]

    if not cu_adevar:
        print('   %s: %d mutari procesate, fara adnotari de comparat' % (eticheta, len(randuri)))
        return 0, 0, []

    corecte = len(cu_adevar) - len(gresite)
    print('   %s: %d/%d corecte (%.1f%%)' % (eticheta, corecte, len(cu_adevar),
                                             100.0 * corecte / len(cu_adevar)))
    for r in gresite:
        print('      %s %s: prezis %-4s adevar %-4s (marja %.2f)'
              % (r['set'], r['nume'], r['pozitie'], r['adevar'], r['marja']))

    return corecte, len(cu_adevar), gresite


# 4. marja de incredere
def raport_marje(toate_randurile, prag=1.8, salveaza=True):
    print('\n[4] MARJA DE INCREDERE (scorul celulei castigatoare / al urmatoarei)')

    marje = np.array([r['marja'] for r in toate_randurile])
    print('   mediana %.2f | minim %.2f | sub %.1f: %d mutari din %d'
          % (np.median(marje), marje.min(), prag, int((marje < prag).sum()), len(marje)))

    slabe = sorted(toate_randurile, key=lambda r: r['marja'])[:5]
    print('   cele mai stranse 5 mutari:')
    for r in slabe:
        stare = 'corect' if r['adevar'] in (None, r['pozitie']) else 'GRESIT'
        print('      %-16s %-6s marja %.2f  prezis %-4s  %s'
              % (r['set'], r['nume'], r['marja'], r['pozitie'], stare))

    if salveaza:
        os.makedirs(DIR_DEPANARE, exist_ok=True)
        for r in slabe[:3]:
            vis = deseneaza_grila(r['tabla'], r['ij'])
            if r['adevar']:
                ia, ja = pozitie_la_index(r['adevar'])
                cv.rectangle(vis, (ja * config.CELULA, ia * config.CELULA),
                             ((ja + 1) * config.CELULA, (ia + 1) * config.CELULA),
                             (255, 0, 255), 4)
            cv.imwrite(os.path.join(DIR_DEPANARE, 'marja_%s_%s.png' % (r['set'].replace(' ','_'), r['nume'])),
                       cv.resize(vis, (900, 900)))
        print('   am salvat imaginile lor in %s' % DIR_DEPANARE)
        print('   (verde = ce am prezis, mov = adnotarea)')

    return marje


def salveaza_greselile(gresite):
    if not gresite:
        return
    os.makedirs(DIR_DEPANARE, exist_ok=True)
    for r in gresite:
        vis = deseneaza_grila(r['tabla'], r['ij'])
        ia, ja = pozitie_la_index(r['adevar'])
        cv.rectangle(vis, (ja * config.CELULA, ia * config.CELULA),
                     ((ja + 1) * config.CELULA, (ia + 1) * config.CELULA),
                     (255, 0, 255), 6)
        cv.imwrite(os.path.join(DIR_DEPANARE, 'greseala_%s_%s.png' % (r['set'].replace(' ','_'), r['nume'])),
                   cv.resize(vis, (900, 900)))
    print('   imaginile greselilor sunt in %s (verde = prezis, mov = adevar)' % DIR_DEPANARE)


def main():
    p = argparse.ArgumentParser(description='verificari pentru Task 1')
    p.add_argument('--jocuri', type=int, nargs='+', default=[1, 2, 3, 4])
    p.add_argument('--scurt', action='store_true', help='sari peste verificarea detectiei')
    args = p.parse_args()

    dir_fake = os.path.join(config.DIR_DATE, 'evaluare', 'fake_test')
    dir_fake_gt = os.path.join(config.DIR_DATE, 'evaluare', 'cod_evaluare', 'fake_test_gt')

    # 1. detectia tablei
    if not args.scurt:
        cai = sorted(glob.glob(os.path.join(config.DIR_ANTRENARE, '*.jpg')))
        cai += sorted(glob.glob(os.path.join(config.DIR_AUXILIARE, '*.jpg')))
        if os.path.isdir(dir_fake):
            cai += sorted(glob.glob(os.path.join(dir_fake, '*.jpg')))
        verifica_detectia_tablei(cai)

    toate = []
    corecte_total = total_total = 0
    gresite_total = []

    # 2. antrenare
    print('\n[2] ACURATETE PE ANTRENARE')
    gasit = False
    for joc in args.jocuri:
        randuri = ruleaza_cu_marje(config.DIR_ANTRENARE, joc, config.DIR_ANTRENARE,
                                   eticheta='antrenare joc %d' % joc)
        if randuri is None:
            continue
        gasit = True
        c, t, g = raport_joc(randuri, 'jocul %d' % joc)
        corecte_total += c
        total_total += t
        gresite_total += g
        toate += randuri
    if not gasit:
        print('   nu am gasit imagini de antrenare')

    # 3. fake_test
    print('\n[3] ACURATETE PE FAKE_TEST (joc nefolosit la reglaje)')
    if os.path.isdir(dir_fake) and os.path.isdir(dir_fake_gt):
        randuri = ruleaza_cu_marje(dir_fake, 1, dir_fake_gt, eticheta='fake_test')
        if randuri:
            c, t, g = raport_joc(randuri, 'fake_test')
            corecte_total += c
            total_total += t
            gresite_total += g
            toate += randuri
    else:
        print('   nu am gasit folderul fake_test')

    # 4. marje
    if toate:
        raport_marje(toate)

    salveaza_greselile(gresite_total)

    print('\n' + '=' * 58)
    if total_total:
        print('TOTAL: %d/%d pozitii corecte (%.1f%%)'
              % (corecte_total, total_total, 100.0 * corecte_total / total_total))
        print('La 200 de imagini de test asta ar insemna %.2f puncte din 5'
              % (5.0 * corecte_total / total_total))
    print('=' * 58)


if __name__ == '__main__':
    main()