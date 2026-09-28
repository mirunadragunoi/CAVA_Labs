# DETECTIA TABLEI DE JOC SI TRECEREA INTRE COORDONATE DE IMAGINI SI COORDONATE DE TABLA
# randurile sunt de la 1 la 14 iar coloanele de la A la N

import re 
import numpy as np
import cv2 as cv 

from config import N, CELULA, DIM, SCALA_DETECTIE, MARGINE_CELULA


# GASIREA GRILEI DE JOC 

def detecteaza_colturi(img):
    """
    intorc cele 4 colturi ale grilei de 14 pe 14 in coordonatele imaginii originale
    ordine: stanga sus, dreapta sus, dreapta jos, stanga jos

    celulele grilei sunt pale gen bleu deschis, crem, alb, in timp ce restul tablei este albastru saturat, iar masa este maro 
    deci caut pixelii cu saturatie mica si luminozitate mare 
    """

    mica = cv.resize(img, (0, 0), fx = SCALA_DETECTIE, fy = SCALA_DETECTIE)
    hsv = cv.cvtColor(mica, cv.COLOR_BGR2HSV)
    _, s, v = cv.split(hsv)

    # pixelii pali sunt putin colorati si luminosi 
    pale = ((s < 110) & (v > 140)).astype(np.uint8) * 255

    # OPEN --->>> sterg structurile subtiri (scrisul, coloana cu nr de piese din dreapta)
    # CLOSE ---->> lipesc apoi celulele palide intre ele, peste patratele albastre, mov si portocalii din interiorul grilei, ca grila sa ajunga o singura pata compacta

    pale = cv.morphologyEx(pale, cv.MORPH_OPEN, np.ones((13, 13), np.uint8))
    pale = cv.morphologyEx(pale, cv.MORPH_CLOSE, np.ones((45, 45), np.uint8))

    contururi, _ = cv.findContours(pale, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contururi:
        raise ValueError("nu am gasit grila de joc in imaginea data")

    contur = max(contururi, key = cv.contourArea)

    # minAreaRect suporta si o mica rotatie a tablei fata de camera 
    cutie = cv.boxPoints(cv.minAreaRect(contur)) / SCALA_DETECTIE

    # ordonez colturile 
    # suma x+y este minima pt stanga sus si maxima jos dreapta
    # diferenta y-x este minima pt dreapta sus si maxima jos stanga 
    suma = cutie.sum(axis = 1)
    dif = np.diff(cutie, axis = 1).ravel()

    return np.array([cutie[np.argmin(suma)], cutie[np.argmin(dif)], cutie[np.argmax(suma)], cutie[np.argmax(dif)]], dtype = np.float32)


def indreapta_tabla(img):
    # aduc grila de joc intr un patrat de 1400 pe 1400 pixeli cu celule de 100 pe 100 
    
    sursa = detecteaza_colturi(img)
    destinatie = np.array([[0, 0], [DIM - 1, 0], [DIM - 1, DIM - 1], [0, DIM - 1]],dtype=np.float32)

    M = cv.getPerspectiveTransform(sursa, destinatie)
    return cv.warpPerspective(img, M, (DIM, DIM))


# functii pentru celule si pozitii

def decupeaza_celula(tabla, i, j, margine = MARGINE_CELULA):
    # interiorul celulei de pe randul i si coloana j ambele fiind de la 0
    return tabla[i * CELULA + margine:(i + 1) * CELULA - margine, j * CELULA + margine:(j + 1) * CELULA - margine]

def index_la_pozitie(i, j):
    # transform din 0 0 in 1A
    return '%d%s' % (i + 1, chr(ord('A') + j))

def pozitie_la_index(pozitie):
    # transform din 9H in 8,7
    m = re.match(r'^(\d{1,2})([A-N])$', pozitie.strip())

    if not m:
        raise ValueError('pozitie invalida: %r' % pozitie)

    return int(m.group(1)) - 1, ord(m.group(2)) - ord('A')


# ajutor pt depanare
def deseneaza_grila(tabla, evidentiaza = None):
    # copie a tablei indreptate cu grila desenata peste si eventual cu o celula incadrata
    vis = tabla.copy()

    for k in range(N + 1):
        cv.line(vis, (k * CELULA, 0), (k * CELULA, DIM - 1), (0, 0, 255), 2)
        cv.line(vis, (0, k * CELULA), (DIM - 1, k * CELULA), (0, 0, 255), 2)

    if evidentiaza is not None:
        i, j = evidentiaza
        cv.rectangle(vis, (j * CELULA, i * CELULA), ((j + 1) * CELULA, (i + 1) * CELULA), (0, 255, 0), 8)

    return vis
