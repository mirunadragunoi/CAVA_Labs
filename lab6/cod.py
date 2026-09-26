import os
import numpy as np
import cv2 as cv


AFISEAZA = True
DIM_CAREU = 810   # 9 celule ori 90 pixeli
DIM_CELULA = DIM_CAREU // 9 

def show_image(title,image):
    if not AFISEAZA:
        return
    image=cv.resize(image,(0,0),fx=0.3,fy=0.3)
    cv.imshow(title,image)
    cv.waitKey(0)
    cv.destroyAllWindows()


# PASUL 1a - extragerea careului
def extrage_careu(image):

    """
        gasesc careul sudoku in imagine si il indrept intr un patrat de 810 pe 810 pixeli prin transformare de perspectiva 
        intorc imaginea color indreptata ca sa pot desena linii colorate peste ea si ca sa pot decupa celulele originale pt cifre
    """

    original = image.copy()

    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    image_m_blur = cv.medianBlur(image,3)
    image_g_blur = cv.GaussianBlur(image_m_blur, (0, 0), 5) 
    image_sharpened = cv.addWeighted(image_m_blur, 1.2, image_g_blur, -0.8, 0)

    show_image('image_sharpened',image_sharpened)

    # PAS 1!!!
    # separ hartia (luminoasa) de fundal (inchis) prin thresholding 
    _, hartie = cv.threshold(image_sharpened, 30, 255, cv.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    hartie = cv.erode(hartie, kernel)
    show_image('image_thresholded', hartie)

    # PAS 2!!!
    # masca de mai sus are gauri exact acolo unde sunt liniile careului
    # ele sunt inchise la culoare, deci cad sub prag
    # umplu masca pastrand doar conturul exterior al foii
    contururi_hartie, _ = cv.findContours(hartie, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contururi_hartie) == 0:
        raise ValueError('nu am gasit foaia in imagine')
    contur_foaie = max(contururi_hartie, key = cv.contourArea)

    hartie_plina = np.zeros_like(hartie)
    cv.drawContours(hartie_plina, [contur_foaie], -1, 255, -1)

    # PAS 3!!!
    # restang masca spre interior, ca sa scap de marginea foii
    # altfel conturul cel mai mare ar fi foaia intreaga, nu careul
    raza = max(3, int(0.01 * max(image.shape)))
    hartie_interior = cv.erode(hartie_plina, np.ones((raza, raza), np.uint8))
    show_image('hartie_interior', hartie_interior)

    # PAS 4!!!
    # in interiorul foii, cerneala (adica liniile careului si cifrele) este inchisa
    # prag adaptiv, ca sa nu ma incurce iluminarea neuniforma din poza
    cerneala = cv.adaptiveThreshold(image_sharpened, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 31, 10)

    cerneala = cv.bitwise_and(cerneala, hartie_interior)

    # ingros putin liniile ca sa fie sigur conectate intre ele
    cerneala = cv.dilate(cerneala, np.ones((3, 3), np.uint8))
    show_image('cerneala', cerneala)

    # PAS 5!!!
    # cel mai mare contur exterior este chenarul careului
    # liniile lui formeaza o singura componenta conexa
    contours, _ = cv.findContours(cerneala, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    max_area = 0
    top_left = top_right = bottom_left = bottom_right = None
   
    for i in range(len(contours)):

        if(len(contours[i]) >3):
            possible_top_left = None
            possible_bottom_right = None

            for point in contours[i].squeeze():
                # suma x+y este minima in contul stanga-sus si maxima in dreapta-jos
                if possible_top_left is None or point[0] + point[1] < possible_top_left[0] + possible_top_left[1]:
                    possible_top_left = point

                if possible_bottom_right is None or point[0] + point[1] > possible_bottom_right[0] + possible_bottom_right[1] :
                    possible_bottom_right = point

            # diferenta y-x este minima in dreapta sus si maxima in stanga jos
            diff = np.diff(contours[i].squeeze(), axis = 1)

            possible_top_right = contours[i].squeeze()[np.argmin(diff)]
            possible_bottom_left = contours[i].squeeze()[np.argmax(diff)]

            arie = cv.contourArea(np.array([[possible_top_left],[possible_top_right],[possible_bottom_right],[possible_bottom_left]]))

            if arie > max_area:
                max_area = arie
                top_left = possible_top_left
                bottom_right = possible_bottom_right
                top_right = possible_top_right
                bottom_left = possible_bottom_left

    if top_left is None:
        raise ValueError('nu am gasit niciun contur potrivit pentru careu')

    if AFISEAZA:
        image_copy = cv.cvtColor(image.copy(), cv.COLOR_GRAY2BGR)
        for colt in [top_left, top_right, bottom_left, bottom_right]:
            cv.circle(image_copy, tuple(colt), 20, (0, 0, 255), -1)
        show_image('detected corners', image_copy)

    # PAS 6!!!
    # transformarea de perspectiva: cele 4 colturi gasite defin cele 4 colturi ale unui patrat de 810 pe 810
    width = DIM_CAREU
    height = DIM_CAREU

    puzzle = np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')
    destination = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')

    M = cv.getPerspectiveTransform(puzzle, destination)
    result = cv.warpPerspective(original, M, (width, height))
    
    return result

# liniile sunt multipli de 90
# lines_vertical dau coordonata pe orizontala (coloana)
# lines_horizontal sau coordonata pe verticala (linia)
# decuparea unei celule: imagine[linii, coloane]

def construieste_linii():
    lines_horizontal = []

    for i in range(0, DIM_CAREU + 1, DIM_CELULA):
        lines_horizontal.append([(0, i), (DIM_CAREU - 1, i)])

    lines_vertical = []

    for i in range(0, DIM_CAREU + 1, DIM_CELULA):
        lines_vertical.append([(i, 0), (i, DIM_CAREU - 1)])

    return lines_horizontal, lines_vertical


def binarizeaza_careu(result):
    # din careul indreptat obtin o imagine binara in care cerneala este alba
    # pe aceasta imagine masor cat de plina este fiecare celula

    gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (5, 5), 0)

    thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 31, 10)

    return thresh


def decupeaza_celula(imagine, lines_horizontal, lines_vertical, i, j, margine=12):
    # decupez celula (i, j) fara chenar
    
    y_min = lines_vertical[j][0][0]
    y_max = lines_vertical[j + 1][1][0]
    x_min = lines_horizontal[i][0][1]
    x_max = lines_horizontal[i + 1][1][1]

    patch = imagine[x_min + margine:x_max - margine, y_min + margine:y_max - margine].copy()

    return patch


# PASUL 1B!!!!!!!!
# PASUL 3!!!! configuratia 0 si X
# pt fiecare celula calculez media intensitatii pe imaginea binarizata, unde cerneala e alba
# o celula goala are media aproape 0, celula cu cifra are media mult mai mare
# pt a fixa pragul: sortez cele 81 de medii si caut cel mai mare salt intre 2 val consecutive

def medii_celule(thresh, lines_horizontal, lines_vertical):
    # media intensitatii pentru fiecare dintre cele 81 de celule, o folosesc ca sa aleg pragul
    medii = np.zeros((9, 9))

    for i in range(9):
        for j in range(9):
            patch = decupeaza_celula(thresh, lines_horizontal, lines_vertical, i, j)
            medii[i, j] = np.mean(patch)

    return medii 

def alege_prag(medii):
    # pragul il aleg automat din datele imaginii

    valori = np.sort(medii.flatten())
    salturi = np.diff(valori)
    k = int(np.argmax(salturi))

    return (valori[k] + valori[k + 1]) / 2

def determina_configuratie_careu_ox(thresh, lines_horizontal, lines_vertical, prag = None):

    matrix = np.empty((9,9), dtype='str')

    medii = medii_celule(thresh, lines_horizontal, lines_vertical)

    if prag is None:
        prag = alege_prag(medii)

    for i in range(len(lines_horizontal) - 1):
        for j in range(len(lines_vertical) - 1):
            # celula are mai multa cerneala --->>> inseamna ca contine o cifra
            matrix[i][j] = 'x' if medii[i, j] > prag else 'o'
            
    return matrix

def vizualizare_configuratie(result, matrix, lines_horizontal, lines_vertical):

    for i in range(len(lines_horizontal) - 1):
        for j in range(len(lines_vertical) - 1):

            y_min = lines_vertical[j][0][0]
            y_max = lines_vertical[j + 1][1][0]
            x_min = lines_horizontal[i][0][1]
            x_max = lines_horizontal[i + 1][1][1]
            
            if matrix[i][j] == 'x': 
                cv.rectangle(result, (y_min, x_min), (y_max, x_max), color=(255, 0, 0), thickness=5)

    return result

# PASUL 4!!! SABLOANE PT CIFRE

DIM_TEMPLATE = 60   # toate cifrele si sabloanele ajung la 60 pe 60
_cache_templates = {}   # sabloanele citite o singura data

def normalizeaza_cifra(patch_bin, dim=DIM_TEMPLATE):
    # decupez cifra de bounding box ul ei si o aduc la o dimensiune fixa
    # fara pasul asta template matching ul compara o cifra din coltul celulei cu un sablon centrat si da scoruri mici pt toate cifrele

    contours, _ = cv.findContours(patch_bin, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None

    c = max(contours, key = cv.contourArea)
    if cv.contourArea(c) < 20:
        return None 

    x, y, w, h = cv.boundingRect(c)
    cifra = patch_bin[y:y + h, x:x + w]

    # o pun intr un patrat ca sa nu se deformeze raportul
    latura = max(w, h)
    patrat = np.zeros((latura, latura), np.uint8)
    off_y = (latura - h) // 2
    off_x = (latura - w) // 2
    patrat[off_y:off_y + h, off_x:off_x + w] = cifra 

    return cv.resize(patrat, (dim, dim), interpolation=cv.INTER_AREA)

def creeaza_templates_din_imagine(cale_imagine, adnotare, director='templates'):
    # construiesc sabloanele decupand cate o aparitie a fiecarei cifre dintr o imagine de antrenare

    os.makedirs(director, exist_ok=True)

    img = cv.imread(cale_imagine)
    result = extrage_careu(img)
    thresh = binarizeaza_careu(result)
    lh, lv = construieste_linii()

    gasite = {}
    for i in range(9):
        for j in range(9):
            c = adnotare[i][j]

            if c == 'o' or c in gasite:
                continue

            patch = decupeaza_celula(thresh, lh, lv, i, j)

            cifra = normalizeaza_cifra(patch)

            if cifra is not None:
                gasite[c] = cifra
                cv.imwrite(os.path.join(director, c + '.jpg'), cifra)

    _cache_templates.pop(director, None)
    return sorted(gasite.keys())

def incarca_templates(director='templates'):
    # citesc sabloanele o singura data si le tin in memorie
    if director in _cache_templates:
        return _cache_templates[director]

    templates = {}

    for j in range(1, 10):
        cale = os.path.join(director, str(j) + '.jpg')

        img_template = cv.imread(cale)

        if img_template is None:
            raise FileNotFoundError('lipseste sablonul %s' % cale)

        img_template = cv.cvtColor(img_template, cv.COLOR_BGR2GRAY)
        _, img_template = cv.threshold(img_template, 127, 255, cv.THRESH_BINARY)
        templates[j] = cv.resize(img_template, (DIM_TEMPLATE, DIM_TEMPLATE))

    _cache_templates[director] = templates
    return templates

def clasifica_cifra(patch, director_templates = 'templates'):
    # compar celula normalizata cu fiecare sablon si aleg cifra cu corelatia cea mai mare

    templates = incarca_templates(director_templates)

    cifra = normalizeaza_cifra(patch)
    if cifra is None:
        return -1

    maxi = -np.inf
    poz = -1

    for j in range(1,10):
        corr = cv.matchTemplate(cifra, templates[j], cv.TM_CCOEFF_NORMED)
        corr = np.max(corr)
        if corr > maxi:
            maxi = corr
            poz = j
        
    return poz

def determina_configuratie_careu_ocifre(img, thresh, lines_horizontal, lines_vertical, prag = None, director_templates = 'templates'):

    matrix = np.empty((9,9), dtype='str')

    medii = medii_celule(thresh, lines_horizontal, lines_vertical)
    if prag is None:
        prag = alege_prag(medii)

    for i in range(len(lines_horizontal) - 1):
        for j in range(len(lines_vertical) - 1):

            if medii[i, j] <= prag:
                matrix[i][j] = 'o'
                continue 

            patch = decupeaza_celula(thresh, lines_horizontal, lines_vertical, i, j)
            cifra = clasifica_cifra(patch, director_templates)
            matrix[i][j] = 'o' if cifra == -1 else str(cifra)
            
    return matrix