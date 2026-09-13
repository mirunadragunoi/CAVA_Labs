import sys
import cv2 as cv
import numpy as np
import copy

from parameters import *
from select_path import *

import pdb

def compute_energy(img):
    """
    calculeaza energia la fiecare pixel pe baza gradientului
    :param img: imaginea initiala
    :return:E - energia
    """
    # ecuatia din articol: energie(I) = modul(derivataI/dx) + modul(derivataI/dy)
    # este norma L1 a gradientului, mare pe muchii si texturi --->> continut important 
    # mica in zone netede cum ar fi cerut peretele apa etc

    # urmati urmatorii pasi:
    # 1. transformati imagine in grayscale
    img_gray = cv.cvtColor(np.float32(img), cv.COLOR_BGR2GRAY)

    # 2. folositi filtru sobel pentru a calcula gradientul in directia X si Y
    grad_x = cv.Sobel(img_gray, cv.CV_64F, 1, 0, ksize=3)
    grad_y = cv.Sobel(img_gray, cv.CV_64F, 0, 1, ksize=3)

    # 3. calculati magnitudinea pentru fiecare pixel al imaginii
    E = np.abs(grad_x) + np.abs(grad_y)

    return E

def show_path(img, path, color):
    new_image = img.copy()
    for row, col in path:
        new_image[row, col] = color

    E = compute_energy(img)

    # normalizez energia in [0, 255] ca sa fie vizibila; altfel valorile
    # mari se satureaza si imaginea iese aproape complet alba
    E_vizibil = cv.normalize(E, None, 0, 255, cv.NORM_MINMAX)

    new_image_E = img.copy()
    new_image_E[:,:,0] = E.copy()
    new_image_E[:,:,1] = E.copy()
    new_image_E[:,:,2] = E.copy()

    for row, col in path:
        new_image_E[row, col] = color
    cv.imshow('path img', np.uint8(new_image))
    cv.imshow('path E', np.uint8(new_image_E))
    cv.waitKey(1000)


def delete_path(img, path):
    """
    elimina drumul vertical din imagine
    :param img: imaginea initiala
    :path - drumul vertical
    return: updated_img - imaginea initiala din care s-a eliminat drumul vertical
    """
    h, w, c = img.shape

    # varianta vectorizata -->> marchez pixelii de sters intr o masca booleana
    # ii scot dintr o data si reasamblez imaginea cu o coloana mai putin
    masca = np.ones((h, w), dtype=bool)
    linii = np.array([p[0] for p in path])
    coloane = np.array([p[1] for p in path])
    masca[linii, coloane] = False 

    updated_img = img[masca].reshape(h, w - 1, c)

    """
        varianta echivalenta cu for
    updated_img = np.zeros((h, w-1, c), img.dtype)
    for i in range(h):
        col = path[i][1]
        updated_img[i, :col] = img[i, :col]
        updated_img[i, col:] = img[i, col + 1:]
    """
        
    return updated_img

def _decrease_width_img(img, num_pixels, params, masca_obiect=None):
    """sterge num_pixels drumuri verticale dintr-o imagine data
 
    lucreaza pe un array, nu pe params, ca sa o putem refolosi la
    amplificarea continutului si la stergerea de obiecte.
 
    masca_obiect: daca este dat, pixelii marcati cu 1 primesc energie foarte
    mica, ca drumurile sa treaca obligatoriu prin ei (folosit la delete_object).
    Masca este taiata odata cu imaginea, ca sa ramana aliniata.
    """
    for i in range(num_pixels):
        print('Eliminam drumul vertical numarul %i dintr-un total de %d.'
              % (i + 1, num_pixels))
 
        E = compute_energy(img)
 
        if masca_obiect is not None:
            # energie puternic negativa => drumul minim este atras in obiect
            E[masca_obiect > 0] = -10 ** 6
 
        path = select_path(E, params.method_select_path)
 
        if params.show_path:
            show_path(img, path, params.color_path)
 
        img = delete_path(img, path)
 
        if masca_obiect is not None:
            # stergem acelasi drum si din masca, ca sa ramana aliniata cu imaginea
            h, w = masca_obiect.shape
            m = np.ones((h, w), dtype=bool)
            m[[p[0] for p in path], [p[1] for p in path]] = False
            masca_obiect = masca_obiect[m].reshape(h, w - 1)
 
    return img, masca_obiect

def decrease_width(params: Parameters, num_pixels):
    img = params.image.copy()  # copiaza imaginea originala
    img, _ = _decrease_width_img(img, num_pixels, params)
    cv.destroyAllWindows()
    return img

def decrease_height(params: Parameters, num_pixels):
    img = params.image.copy()
    img_transpus = np.transpose(img, (1, 0, 2)).copy()
 
    img_transpus, _ = _decrease_width_img(img_transpus, num_pixels, params)
 
    img = np.transpose(img_transpus, (1, 0, 2)).copy()
    cv.destroyAllWindows()
    return img


def delete_object(params: Parameters, x0, y0, w, h):
    #TODO: scrieti codul
    return None

def resize_image(params: Parameters):

    if params.resize_option == 'micsoreazaLatime':
        # redimensioneaza imaginea pe latime
        resized_image = decrease_width(params, params.num_pixels_width)
        return resized_image

    elif params.resize_option == 'micsoreazaInaltime':
        resized_image = decrease_height(params, params.num_pixel_height)
        return resized_image
    
    elif params.resize_option == 'amplificaContinut':
        #TODO: scrieti codul
        return None

    elif params.resize_option == 'eliminaObiect':
        #TODO: scrieti codul
        return None


    else:
        print('The option is not valid!')
        sys.exit(-1)