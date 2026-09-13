import sys
import numpy as np
import pdb


def select_random_path(E):
    # pentru linia 0 alegem primul pixel in mod aleator
    line = 0
    col = np.random.randint(low=0, high=E.shape[1], size=1)[0]
    path = [(line, col)]

    # daca las for ul sa inceapa de la 9, drumul o sa aiba H+1 pixeli, in loc de H si doua pozitii pe prima linie, iar delete_path o sa crape
    # modific ca for ul sa inceapa de la 1

    for i in range(1, E.shape[0]):
        # alege urmatorul pixel pe baza vecinilor
        line = i
        # coloana depinde de coloana pixelului anterior
        if path[-1][1] == 0:  # pixelul este localizat la marginea din stanga
            opt = np.random.randint(low=0, high=2, size=1)[0]
        elif path[-1][1] == E.shape[1] - 1:  # pixelul este la marginea din dreapta
            opt = np.random.randint(low=-1, high=1, size=1)[0]
        else:
            opt = np.random.randint(low=-1, high=2, size=1)[0]
        col = path[-1][1] + opt
        path.append((line, col))

    return path

def select_dynamic_programming_path(E):
    """drumul vertical de cost minim, dupa ecuatia de programare dinamica
    din articol:
 
        M(i, j) = e(i, j) + min( M(i-1, j-1), M(i-1, j), M(i-1, j+1) )
 
    M(i, j) = costul celui mai ieftin drum care porneste de pe prima linie
    si ajunge in pixelul (i, j). La final, minimul de pe ultima linie ne da
    capatul drumului optim, si reconstruim drumul mergand inapoi
    """

    h, w = E.shape
    M = E.astype(np.float64).copy()

    # parinte[i, j] = coloana de pe linia i - 1 din care am ajuns la (i, j)
    parinte = np.zeros((h, w), dtype=np.int32)

    for i in range(1, h):
        linie_anterioara = M[i - 1]

        # construiesc cei 3 vecini ca vectori aliniati ca sa nu iterez dupa j
        # stanga[j] = M[i-1, j-1], centru[j] = M[i-1, j], dreapta[j] = M[i-1, j+1]

        stanga = np.empty(w)
        stanga[0] = np.inf
        stanga[1:] = linie_anterioara[:-1]

        dreapta = np.empty(w)
        dreapta[-1] = np.inf   # pixelul de pe coloana 0 nu are vecin la stanga
        dreapta[:-1] = linie_anterioara[1:]

        vecini = np.vstack([stanga, linie_anterioara, dreapta])
        alegere = np.argmin(vecini, axis=0)    # 0 stanga, 1 centru, 2 dreapta

        M[i] += vecini[alegere, np.arange(w)]

        # alegere - 1 da deplasamentul adica -1 0 sau +1
        parinte[i] = np.arange(w) + alegere - 1

    # capatul drumului optim = minimul de pe ultima linie
    coloana = int(np.argmin(M[h -1]))
    path = [(h-1, coloana)]

    # reconstruiesc drumul inapoi urmarind parintii inapoi, de jos in sus

    for i in range(h - 1, 0, -1):
        coloana = int(parinte[i, coloana])
        path.append((i - 1, coloana))

    path.reverse()   # vrem drumul de sus in jos

    return path

def select_greedy_path(E):
    # implementez si metoda asta deoarece era ceruta in parameters.py
    # prin greedy se alege pe prima linie pixelul de energie minima
    # la fiecare pas coboara in vecinul de energie minima din cei 3 posibili
    # nu garanteaza drumul optim totusi

    h, w = E.shape
    coloana = int(np.argmin(E[0]))
    path = [(0, coloana)]

    for i in range(1, h):
        # vecinii posibili pe linia urmatoare pot fi
        # col - 1, col, col + 1 (taiati la margini)
        start = max(coloana - 1, 0)
        end = min(coloana + 2, w)
        coloana = start + int(np.argmin(E[i, start:end]))
        path.append((i, coloana))

    return path

def select_path(E, method):
    if method == 'aleator':
        return select_random_path(E)
    elif method == 'programareDinamica':
        return select_dynamic_programming_path(E)
    else:
        print('The selected method %s is invalid.' % method)
        sys.exit(-1)