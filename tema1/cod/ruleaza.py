import os
import sys
import argparse

import cv2 as cv

import config
from tabla import indreapta_tabla, deseneaza_grila, pozitie_la_index
from task1 import proceseaza_joc, proceseaza_toate_jocurile
from evalueaza import evalueaza_tot


def cmd_antrenare(args):

    director_iesire = os.path.join(config.DIR_REZULTATE, 'antrenare')

    rezultate = proceseaza_toate_jocurile(config.DIR_ANTRENARE, args.jocuri, director_iesire, verbose=not args.scurt)
    print()
    evalueaza_tot(rezultate, config.DIR_ANTRENARE, verbose=True)

    print('\nfisierele cu predictii sunt in %s' % director_iesire)


def cmd_testare(args):
    director_iesire = os.path.join(config.DIR_REZULTATE, 'testare')
    proceseaza_toate_jocurile(config.DIR_TESTARE, args.jocuri, director_iesire, verbose=not args.scurt)
    print('\nfisierele cu predictii sunt in %s' % director_iesire)


def cmd_verifica(args):

    cale = os.path.join(config.DIR_ANTRENARE, args.imagine + '.jpg')

    if not os.path.exists(cale):
        cale = args.imagine

    img = cv.imread(cale)

    if img is None:
        print('nu gasesc imaginea %s' % cale)
        return

    tabla = indreapta_tabla(img)

    evidentiaza = None
    cale_gt = os.path.splitext(cale)[0] + '.txt'

    if os.path.exists(cale_gt):
        with open(cale_gt) as f:
            evidentiaza = pozitie_la_index(f.read().split()[0])

    os.makedirs(config.DIR_REZULTATE, exist_ok=True)

    iesire = os.path.join(config.DIR_REZULTATE, 'verificare_' + os.path.basename(os.path.splitext(cale)[0]) + '.png')

    cv.imwrite(iesire, deseneaza_grila(tabla, evidentiaza))

    print('am salvat %s' % iesire)
    if evidentiaza:
        print('celula incadrata cu verde este cea din adnotare')


def main():
    p = argparse.ArgumentParser(description='Mathable -->> Task 1')
    sub = p.add_subparsers(dest='comanda')

    pa = sub.add_parser('antrenare', help='ruleaza si evalueaza pe datele de antrenare')
    pa.add_argument('--jocuri', type=int, nargs='+', default=[1, 2, 3, 4])
    pa.add_argument('--scurt', action='store_true', help='nu afisa fiecare mutare')
    pa.set_defaults(func=cmd_antrenare)

    pt = sub.add_parser('testare', help='ruleaza pe datele de testare')
    pt.add_argument('--jocuri', type=int, nargs='+', default=[1, 2, 3, 4])
    pt.add_argument('--scurt', action='store_true')
    pt.set_defaults(func=cmd_testare)

    pv = sub.add_parser('verifica', help='salveaza o tabla indreptata cu grila peste')
    pv.add_argument('imagine', help='ex: 1_01')
    pv.set_defaults(func=cmd_verifica)

    args = p.parse_args()
    if not args.comanda:
        p.print_help()
        return
    args.func(args)


if __name__ == '__main__':
    main()