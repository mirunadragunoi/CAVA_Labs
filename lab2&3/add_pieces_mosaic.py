from parameters import *
import numpy as np
import pdb
import timeit

def culori_medii_piese(small_images):
    # ca sa calculez culoarea medie a fiecarei piese, matrice de norma (N, C)
    # calculez o singura data ca sa am valoarea retinuta
    # axis=(1,2) = media peste inaltime si latime, deci ramane cate o singura valoare pentru fiecare piesa si fiecare canal de culoare
    return np.mean(small_images.astype(np.float64), axis=(1, 2))

def alege_piesa(culoare_medie_patch, culori_piese, criterion, N, exclude=None):
    # intorc indicele piesei alese conform criteriului cerut
    # exclude = lista de indici interzisi (ca sa nu pun doua piese identice una langa alta)

    if criterion == 'aleator':
        if exclude:
            permise = [i for i in range(N) if i not in exclude]
            return int(np.random.choice(permise))
        return int(np.random.randint(low=0, high=N))

    # distanta euclidiana intre culorile medii
    distante = np.sum((culori_piese - culoare_medie_patch) ** 2, axis=1)
    if exclude:
        distante = distante.copy()
        distante[list(exclude)] = np.inf

    return int(np.argmin(distante))


def add_pieces_grid(params: Parameters):
    start_time = timeit.default_timer()
    img_mosaic = np.zeros(params.image_resized.shape, np.uint8)
    N, H, W, C = params.small_images.shape
    h, w, c = params.image_resized.shape
    num_pieces = params.num_pieces_vertical * params.num_pieces_horizontal

    # optional: intezic piese identice pe pozitii vecine
    vecini_diferiti = getattr(params, 'different_neighbors', False)

    if params.criterion == 'aleator':
        for i in range(params.num_pieces_vertical):
            for j in range(params.num_pieces_horizontal):
                pozitie = np.random.randint(low=9, high=N)
                img_mosaic[i * H : (i + 1) * H, j * W : (j + 1) * W, :] = params.small_images[pozitie]
                print('Building mosaic %.2f%%' % (100 * (i * params.num_pieces_horizontal + j + 1) / num_pieces))

    elif params.criterion == 'distantaCuloareMedie':
        culori_piese = culori_medii_piese(params.small_images)

        # retinem ce piesa am pus pe fiecare pozitie pt vecini diferiti
        indici = -np.ones((params.num_pieces_vertical, params.num_pieces_horizontal), dtype=int)

        for i in range(params.num_pieces_vertical):
            for j in range(params.num_pieces_horizontal):
                patch = params.image_resized[i * H : (i + 1) * H, j * W : (j + 1) * W, :]

                # culoarea medie a blocului este media peste linii si coloane
                culoare_patch = np.mean(patch.astype(np.float64), axis=(0, 1))

                exclude = []
                if vecini_diferiti:
                    if i > 0:
                        exclude.append(indici[i - 1, j])  # vecinul de sus
                    if j > 0:
                        exclude.append(indici[i, j - 1])  # vecinul din stanga

                pozitie = alege_piesa(culoare_patch, culori_piese, params.criterion, N, exclude)

                indici[i, j] = pozitie
                img_mosaic[i * H : (i + 1) * H, j * W : (j + 1) * W, :] = params.small_images[pozitie]
                print('Building mosaic %.2f%%' % (100 * (i * params.num_pieces_horizontal + j) / num_pieces))
    else:
        print('Error! unknown option %s' % params.criterion)
        exit(-1)

    end_time = timeit.default_timer()
    print('Running time: %f s.' % (end_time - start_time))

    return img_mosaic


def add_pieces_random(params: Parameters):
    # aranjare aleatoare, cu suprapuneri

    start_time = timeit.default_timer()

    img_mosaic = np.zeros(params.image_resized.shape, np.uint8)
    N, H, W, C = params.small_images.shape
    h, w, c = params.image_resized.shape

    culori_piese = culori_medii_piese(params.small_images)

    # matrice care retine ce pixeli au fost deja acoperiti de cel putin o piesa
    acoperit = np.zeros((h, w), dtype=bool)

    # contor incremental pt a numara np.sum(acoperit) - cati pixeli sunt acoperiti
    neacoperiti = h * w 
    piese_puse = 0

    while neacoperiti > 0:
        # colt stanga sus al piesei
        # il lasam sa fie si negativ pt ca piesa poate atarna peste marginea de sus/din stanga
        # altfel pixelul (0, 0) ar putea fi acoperit de o singura pozitie si bucla nu s ar mai termina

        y = np.random.randint(low = -H + 1, high=h)
        x = np.random.randint(low = -W + 1, high=w)

        # zona efectiv vizibila din mozaic, dupa taierea din margini
        y1, x1 = max(y, 0), max(x, 0)
        y2, x2 = min(y + H, h), min(x + W, w)

        patch = params.image_resized[y1:y2, x1:x2, :]
        culoare_patch = np.mean(patch.astype(np.float64), axis = (0, 1))
        pozitie = alege_piesa(culoare_patch, culori_piese, params.criterion, N)

        # suprascriu efectiv zona
        # suprapunerile sunt permise si chiar dorite
        piesa = params.small_images[pozitie]
        img_mosaic[y1:y2, x1:x2, :] = piesa[y1 - y : y2 - y, x1 - x : x2 - x, :]

        # actualizez doar fereastra mica, nu toata imaginea
        neacoperiti -= int(np.sum(~acoperit[y1:y2, x1:x2]))
        acoperit[y1:y2, x1:x2] = True 

        piese_puse += 1
        if piese_puse % 500 == 0:
            print('Building mosaic %.2f%% (%d piese)' % (100 * (h * w - neacoperiti) / (h * w), piese_puse))


    print('am folosit %d piese' % piese_puse)
    end_time = timeit.default_timer()
    print('running time:', (end_time - start_time), 's')
    return img_mosaic

def construieste_masca_hexagon(H, W):
    # masca binara care taie cele 4 colturi ale piesei dreptunghiulare
    a = W // 4   # latimea portiunii inclinate
    masca = np.zeros((H, W), np.uint8)

    # vf poligon in ordine, format x, y
    puncte = np.array(
        [
            [a, 0],
            [W - 1 - a, 0],
            [W - 1, H // 2],
            [W - 1 - a, H - 1],
            [a, H - 1],
            [0, H // 2]
        ], dtype = np.int32
    )

    cv.fillConvexPoly(masca, puncte, 1)

    # dilatez cu 1 pixel din cauza rotunjirilor la numere intregi laturile inclinate a doua poligoane vecine nu cad pe aceiasi pixeli 
    # asa hexagoanele se suprapun minimal in loc sa lage goluri
    masca = cv.dilate(masca, np.ones((3, 3), np.uint8), iterations=1)
    return masca, a

def add_pieces_hexagon(params: Parameters):
    start_time = timeit.default_timer()

    N, H, W, C = params.small_images.shape
    h, w, c = params.image_resized.shape

    masca, a = construieste_masca_hexagon(H, W)

    # masca pe 3 canale, ca sa o putem folosi la indexare booleana
    masca3 = np.repeat(masca[:, :, np.newaxis], C, axis=2).astype(bool)
    nr_pixeli_masca = int(np.sum(masca))

    # pas orizontal intre doua coloane de hexagoane W - a (3W/4)
    # coloanele impare sunt coborate cu jumatate de inaltime, asa se lipesc hexagoanele perfect, fara goluri
    dx = W - a
    dy = H

    # lucram pe o panza mai mare, ca piesele sa poata iesi peste margini
    pad_y, pad_x = 2 * H, 2 * W 

    img_padded = np.atleast_3d(cv.copyMakeBorder(params.image_resized, pad_y, pad_y, pad_x, pad_x, cv.BORDER_REPLICATE))
    mosaic_padded = np.zeros_like(img_padded)
    ph, pw = mosaic_padded.shape[:2]

    culori_piese = culori_medii_piese(params.small_images)

    nr_coloane = w // dx + 3
    nr_linii = h // dy + 3
    total = nr_coloane * nr_linii

    for j in range(nr_coloane):
        for i in range(nr_linii):
            # pornesc cu o piesa in afara imaginii ca sa fie acoperite complet si colturile stanga sus
            y = pad_y - H + i * dy + (H // 2 if j % 2 == 1 else 0)
            x = pad_x - W + j * dx 

            if y < 0 or x < 0 or y + H > ph or x + W > pw:
                continue 

            patch = img_padded[y : y + H, x : x + W, :].astype(np.float64)

            # media doar pe pixelii din interiorul hexagonului
            culoare_patch = np.sum(patch * masca3, axis=(0, 1)) / nr_pixeli_masca
            pozitie = alege_piesa(culoare_patch, culori_piese, params.criterion, N)

            # copiez doar pixelii din interiorul hexagonului
            regiune = mosaic_padded[y : y + H, x : x + W, :]
            regiune[masca3] = params.small_images[pozitie][masca3]

            print('Building mosaic %.2f%%' % (100 * (j * nr_linii + i + 1) / total))

    # tai inapoi la dimensiunea mozaicului
    img_mosaic = mosaic_padded[pad_y : pad_y + h, pad_x : pad_x + w, :]

    end_time = timeit.default_timer()
    print('running time:', (end_time - start_time), 's')
    return img_mosaic