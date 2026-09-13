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

# factorul de amplificare al continutului
params.factor_amplification = 1.2

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

def sterg_obiecte(nume_imagine, director_date='../data/', director_iesire='./rezultate/', nr_incercari=5):
    os.makedirs(director_iesire, exist_ok=True)

    def salvez(nume, img):
        cv.imwrite(os.path.join(director_iesire, nume), np.uint8(np.clip(img, 0, 255)))

    cale = os.path.join(director_date, nume_imagine)
    scurt = os.path.splitext(nume_imagine)[0]

    for k in range(nr_incercari):
        # reincarc imaginea initiala de fiecare data ca sa pornesc mereu de la original
        p = Parameters(cale)
        p.show_path = False
        p.method_select_path = 'programareDinamica'

        # selectROI are nevoie de uint8 iar params.image este float32
        pentru_selectie = np.uint8(np.clip(p.image, 0, 255))

        titlu = 'incercarea %d din %d - ENTER = confirm, ESC = gata' % (k + 1, nr_incercari)

        x0, y0, w, h = cv.selectROI(titlu, pentru_selectie, showCrosshair=False)
        cv.destroyAllWindows()

        # daca apas pe ESX sau nu trag dreptunghi selectROI intoarce zerouri
        if w == 0 or h == 0:
            print('m-am oprit la incercarea %d.' % (k + 1))
            break

        x0, y0, w, h = int(x0), int(y0), int(w), int(h)

        print('incercarea %d: sterg dreptunghiul x=%d y=%d w=%d h=%d (%s drumuri).' % (k + 1, x0, y0, w, h, 'verticale' if w <= h else 'orizontale'))

        # salvez originalul cu selectia marcata pentru documentatie
        marcat = pentru_selectie.copy()
        cv.rectangle(marcat, (x0, y0), (x0 + w, y0 + h), (0, 0, 255), 2)
        salvez('%s_obiect_%d_selectie.png' % (scurt, k + 1), marcat)

        # apelez direct delete_object
        rezultat = delete_object(p, x0, y0, w, h)

        nume_rezultat = '%s_obiect_%d_x%d_y%d_w%d_h%d.png' % (scurt, k + 1, x0, y0, w, h)
        salvez(nume_rezultat, rezultat)
        print('   am salvat %s  (%s -> %s)' % (nume_rezultat, str(p.image.shape[:2]), str(rezultat.shape[:2])))

    cv.destroyAllWindows()

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

    # PASUL 3!!!! --->> amplificarea continutului cu mai multi factori
    for f in [1.05, 1.1, 1.2, 1.3]:
        p = Parameters(os.path.join(director_date, 'arcTriumf.jpg'))
        p.show_path = False
        p.method_select_path = 'programareDinamica'
        p.resize_option = 'amplificaContinut'
        p.factor_amplification = f
        salvez('arcTriumf_amplificat_%.2f.png' % f, resize_image(p))

    # PASUL 4!!! -->> sa sterg un obiect din imagine
    sterg_obiecte('lac.jpg')
    
rulez_pasi()