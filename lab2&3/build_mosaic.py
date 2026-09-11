import os
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pdb

from add_pieces_mosaic import *
from parameters import *


def load_pieces(params: Parameters):
    # citeste toate cele N piese folosite la mozaic din directorul corespunzator
    # toate cele N imagini au aceeasi dimensiune H x W x C, unde:
    # H = inaltime, W = latime, C = nr canale (C=1  gri, C=3 color)
    # functia intoarce pieseMozaic = matrice N x H x W x C in params
    # pieseMoziac[i, :, :, :] reprezinta piesa numarul i


    # citeste imaginile din director
    images = []
    nume_fisiere = sorted(os.listdir(params.small_images_dir))
    extensie = '.' + params.image_type.lower()

    for nume in nume_fisiere:
        if not nume.lower().endswith(extensie):
            continue

        img = cv.imread(os.path.join(params.small_images_dir, nume))

        if img is None:
            continue

        # daca imaginea de referinta este grayscale, convertesc si piesele
        if params.image.ndim == 2:
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # atleast_3d transforma (H, W) in (H, W, 1) ca sa avem mereu 4 axe
        images.append(np.atleast_3d(img))

    if len(images) == 0:
        print('nu am gasit imagini cu extensia %s in %s' %
                (params.image_type, params.small_images_dir)
              )
        exit(-1)

    if params.show_small_images:
        for i in range(10):
            for j in range(10):
                if i * 10 + j >= len(images):
                    break

                plt.subplot(10, 10, i * 10 + j + 1)
                plt.axis('off')

                # OpenCV reads images in BGR format, matplotlib reads images in RBG format
                im = images[i * 10 + j].copy()

                if im.shape[2] == 3:
                    # BGR to RGB, swap the channels
                    im = im[:, :, [2, 1, 0]]
                    plt.imshow(im)
                else:
                    plt.imshow(im[:, :, 0], cmap = 'gray')
                
        plt.show()

    params.small_images = np.array(images)


def compute_dimensions(params: Parameters):
    # calculeaza dimensiunile mozaicului
    # obtine si imaginea de referinta redimensionata avand aceleasi dimensiuni
    # ca mozaicul

    hs, ws = params.small_images.shape[1], params.small_images.shape[2]
    params.image = np.atleast_3d(params.image)
    h, w = params.image.shape[0], params.image.shape[1]

    # latimea mozaicului = nr piese pe orizontala ori latimea unei piese
    # iese exact, fara resturi, ca piesele sa se potriveasca perfect
    new_w = params.num_pieces_horizontal * ws 

    # calculeaza automat numarul de piese pe verticala
    # pastrez raportul latime/inaltime al imaginii originale
    new_h = new_w * h / w
    params.num_pieces_vertical = int(round(new_w / hs))

    if params.num_pieces_vertical < 1:
        params.num_pieces_vertical = 1

    # rotunjesc inaltimea la un multiplu exact de hs
    new_h = params.num_pieces_vertical * hs

    # redimensioneaza imaginea
    # atentie!!! cv.resize primeste (latime, inaltime)
    params.image_resized = np.atleast_3d(cv.resize(params.image, (new_w, new_h)))

    print('mozaic de %d x %d piese, imaginea redimensionata la %s!!' %
          (
              params.num_pieces_vertical, params.num_pieces_horizontal, params.image_resized.shape
          ))



def build_mosaic(params: Parameters):
    # incarcam imaginile din care vom forma mozaicul
    load_pieces(params)
    # calculeaza dimensiunea mozaicului
    compute_dimensions(params)

    img_mosaic = None
    if params.layout == 'caroiaj':
        if params.hexagon is True:
            img_mosaic = add_pieces_hexagon(params)
        else:
            img_mosaic = add_pieces_grid(params)
    elif params.layout == 'aleator':
        img_mosaic = add_pieces_random(params)
    else:
        print('Wrong option!')
        exit(-1)

    return img_mosaic