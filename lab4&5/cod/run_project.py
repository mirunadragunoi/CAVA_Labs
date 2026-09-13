"""
    PROIECT
    REDIMENSIONEAZA IMAGINI.
    Implementarea a proiectului Redimensionare imagini
    dupa articolul "Seam Carving for Content-Aware Iamge Resizing", autori S. Avidan si A. Shamir
"""

from parameters import *
from resize_image import *
import matplotlib.pyplot as plt
import os

image_name = '../data/castel.jpg'
params = Parameters(image_name)

# seteaza optiunea de redimenionare
# micsoreazaLatime, micsoreazaInaltime, amplificaContinut, eliminaObiect
params.resize_option = 'micsoreazaLatime'

# numarul de pixeli pe latime
params.num_pixels_width = 50

# numarul de pixeli pe inaltime
params.num_pixel_height = 50

# afiseaza drumul eliminat
params.show_path = True

# metoda pentru alegerea drumului
# aleator, greedy, programareDinamica
params.method_select_path = 'aleator'

resized_image = resize_image(params)
resized_image_opencv = cv.resize(params.image, (resized_image.shape[1], resized_image.shape[0]))

# imaginile sunt float32 si BGR de aia le convertesc la uint8 si inversez canalele
def pentru_afisare(img):
    return np.uint8(np.clip(img, 0, 255))[:, :, [2, 1, 0]]

plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(pentru_afisare(params.image))
plt.xlabel('original')

plt.subplot(1, 3, 2)
plt.imshow(pentru_afisare(resized_image_opencv))
plt.xlabel('OpenCV')

plt.subplot(1, 3, 3)
plt.imshow(pentru_afisare(resized_image))
plt.xlabel('My result')

cv.imwrite('rezultat.png', np.uint8(np.clip(resized_image, 0, 255)))
plt.show()

def rulez_pasi(director_date='../data/', director_iesire='./rezultate/'):
    os.makedirs(director_iesire, exist_ok=True)

    def salvez(nume, img):
        cv.imwrite(os.path.join(director_iesire, nume), np.uint8(np.clip(img, 0, 255)))

    # PASUL 1!!!!!!!
    # imaginea cu castel 
    # imaginea initiala, imaginea redimensionata la o imagine cu 50 de pixeli mai putini in latime folosind algoritmul de pastrare al continutului
    # imaginea initiala redimensionata la o imagine cu 50 de pixeli mai putini in latime cu algoritmul de redimensionare uzuala cu resize din OpenCV
    # testez pe imaginea cu castelul eliminand 50, 75 si 100 de pixeli in latime

    for n in [50, 75, 100]:
        p = Parameters(os.path.join(director_date, 'castel.jpg'))
        p.show_path = False
        p.method_select_path = 'programareDinamica'
        p.resize_option = 'micsoreazaLatime'
        p.num_pixels_width = n 
        salvez('castel_latime_%d.png' % n, resize_image(p))

    # comparatie intre cele trei metode de alegere a drumului 
    for metoda in ['aleator', 'greedy', 'programareDinamica']:
        p = Parameters(os.path.join(director_date, 'castel.jpg'))
        p.show_path = False
        p.method_select_path = metoda
        p.resize_option = 'micsoreazaLatime'
        p.num_pixels_width = 50
        salvez('castel_metoda_%s.png' % metoda, resize_image(p))

    # PASUL 2!!!!!!! --->> imaginea cu praga pentru micsorarea inaltimei
    for n in [50, 75, 100]:
        p = Parameters(os.path.join(director_date, 'praga.jpg'))
        p.show_path = False
        p.method_select_path = 'programareDinamica'
        p.resize_option = 'micsoreazaInaltime'
        p.num_pixel_height = n
        salvez('praga_inaltime_%d.png' % n, resize_image(p))

rulez_pasi()