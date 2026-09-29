# TASK 1 TEMA
# GASIREA POZITIEI PIESEI ADAUGATE LA FIECARE MUTARE

# idee de baza: intre doua mutari consecutive se schimba o singura celula, cea pe care s a pus piesa
# deci nu incerc sa recunosc o piesa in absolut, doar compar imaginea curenta cu cea precedenta si caut celula care s a schimbat cel mai mult

import os
import glob
import numpy as np
import cv2 as cv

from config import N, CELULA, MARGINE_CELULA, IMAGINE_TABLA_GOALA, DIR_REZULTATE
from tabla import indreapta_tabla, decupeaza_celula, index_la_pozitie

def scoruri_schimbare(tabla_acum, tabla_inainte):
    # vad cat de mult s a schimbat fiecare celula cu matrice 14 pe 14
    # lucrez pe imaginile in tonuri de gri

    a = cv.cvtColor(tabla_acum, cv.COLOR_BGR2GRAY).astype(np.float32)
    b = cv.cvtColor(tabla_inainte, cv.COLOR_BGR2GRAY).astype(np.float32)

    dif = np.abs(a - b)

    scoruri = np.zeros((N, N), dtype = np.float32)

    for i in range(N):
        for j in range(N):
            scoruri[i, j] = decupeaza_celula(dif, i, j).mean()

    return scoruri

def gaseste_piesa_noua(tabla_acum, tabla_inainte, ocupate = None):
    # intoarce (i, j, scoruri) pt celula in care s a pus piesa
    # ocupate: set de celule deja ocupate --->> le exclud pentru ca o piesa nu se pune niciodata peste alta piesa
    
    scoruri = scoruri_schimbare(tabla_acum, tabla_inainte)

    scoruri_filtrate = scoruri.copy()
    if ocupate:
        for (i, j) in ocupate:
            scoruri_filtrate[i, j] = -1

    i, j = np.unravel_index(np.argmax(scoruri_filtrate), scoruri_filtrate.shape)

    return int(i), int(j), scoruri 


def incredere(scoruri, i, j):
    # raportul dintre scorul castigator si urmatorul
    # cu cat e mai mare, cu atat mai sigur 
    # il folosesc doar ca sa semnalez mutarile dubioase

    v = np.sort(scoruri.ravel())[::-1]
    return float(v[0] / max(v[1], 1e-6))

# RULAREA PE UN JOC INTREG

def imagini_joc(director, joc):
    # caile imaginilor unui joc, in ordinea mutarilor
    tipar = os.path.join(director, '%d_*.jpg' % joc)

    return sorted(f for f in glob.glob(tipar) if os.path.basename(f).split('_')[1][0].isdigit())

def proceseaza_joc(director, joc, director_iesire = None, verbose = True):
    # ruleaza task1 pe toate muturaile unui joc 
    # intoarce lista de (nume_imagine, pozitie, i, j)

    cai = imagini_joc(director, joc)
    if not cai:
        raise FileNotFoundError('nu am gasit imagini pentru jocul %d in %s' % (joc, director))

    if verbose:
        print('jocul %d: %d imagini' % (joc, len(cai)))

    # referinta pentru prima mutare: tabla goala
    tabla_goala = cv.imread(IMAGINE_TABLA_GOALA)

    if tabla_goala is None:
        raise FileNotFoundError('lipeste imaginea cu tabla goala: %s' % IMAGINE_TABLA_GOALA)

    tabla_inainte = indreapta_tabla(tabla_goala)

    ocupate = set()
    rezultate = []

    for cale in cai:
        nume = os.path.splitext(os.path.basename(cale))[0]
        img = cv.imread(cale)

        if img is None:
            raise FileNotFoundError(cale)

        tabla_acum = indreapta_tabla(img)

        i, j, scoruri = gaseste_piesa_noua(tabla_acum, tabla_inainte, ocupate)
        pozitie = index_la_pozitie(i, j)

        ocupate.add((i, j))
        rezultate.append((nume, pozitie, i, j))

        if verbose:
            inc = incredere(scoruri, i, j)
            semn = '' if inc > 1.8 else '   <-- incredere mica (%.2f)' % inc 
            print('   %s -> %-4s%s' % (nume, pozitie, semn))

        # tabla curenta devine referinta pentru mutarea urmatoare
        tabla_inainte = tabla_acum

    if director_iesire:
        scrie_rezultate(rezultate, director_iesire)

    return rezultate

def scrie_rezultate(rezultate, director_iesire):
    # scrie cate un fisier .txt per mutare in formatul cerut de codul de evaluare

    # pt task 1 nu ma intereseaza valoarea, doar codul de evaluare face line.split() si asteapta doua campuri, deci pun '0' ca sa nu crape

    os.makedirs(director_iesire, exist_ok=True)
    for nume, pozitie, _, _ in rezultate:
        with open(os.path.join(director_iesire, nume + '.txt'), 'w') as f:
            f.write('%s 0' % pozitie)


def proceseaza_toate_jocurile(director, jocuri = (1, 2, 3, 4), director_iesire=None, verbose=True):
    toate = {}
    for joc in jocuri:
        try:
            toate[joc] = proceseaza_joc(director, joc, director_iesire, verbose)

        except FileNotFoundError as e:
            if verbose:
                print('sar peste jocul %d: %s' % (joc, e))
                
    return toate