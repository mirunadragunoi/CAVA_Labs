"""
    PROIECT
    REDIMENSIONEAZA IMAGINI.
    Implementarea a proiectului Redimensionare imagini
    dupa articolul "Seam Carving for Content-Aware Image Resizing", autori S. Avidan si A. Shamir
"""

from parameters import *
from resize_image import *
import matplotlib.pyplot as plt
import os
import sys

DIRECTOR_DATE = '../data/'
DIRECTOR_IESIRE = './rezultate/'

# daca e True se afiseaza fiecare drum eliminat la 1 sec
SHOW_PATH = False

# functiile de care mai am nevoie

# imaginile sunt float32 si BGR de aia le convertesc la uint8 si inversez canalele
def pentru_afisare(img):
    return np.uint8(np.clip(img, 0, 255))[:, :, [2, 1, 0]]

def salvez(nume, img):
    os.makedirs(DIRECTOR_IESIRE, exist_ok=True)
    cv.imwrite(os.path.join(DIRECTOR_IESIRE, nume), np.uint8(np.clip(img, 0, 255)))
    print('       ! am salvat %s' % nume)

def parametri(nume_imagine, **setari):
    # construiesc Parameters cu setarile pe care le folosesc peste tot ca sa nu mai repet
    p = Parameters(os.path.join(DIRECTOR_DATE, nume_imagine))
    p.show_path = SHOW_PATH
    p.method_select_path = 'programareDinamica'

    for cheie, valoare in setari.items():
        setattr(p, cheie, valoare)

    return p

def salvez_varianta_opencv(nume_baza, p, rezultat):
    # salvez si varianta redimensionata uzual la aceleasi dimensiuni pt comparatie 
    opencv = cv.resize(p.image, (rezultat.shape[1], rezultat.shape[0]))
    salvez(nume_baza + '_opencv.png', opencv)


# demo ul efectiv 
def demo_vizual():
    p = parametri('castel.jpg', resize_option='micsoreazaLatime', num_pixels_width=50, method_select_path='aleator')
 
    rezultat = resize_image(p)
    rezultat_opencv = cv.resize(p.image, (rezultat.shape[1], rezultat.shape[0]))
 
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    plt.imshow(pentru_afisare(p.image))
    plt.xlabel('original')
 
    plt.subplot(1, 3, 2)
    plt.imshow(pentru_afisare(rezultat_opencv))
    plt.xlabel('OpenCV')
 
    plt.subplot(1, 3, 3)
    plt.imshow(pentru_afisare(rezultat))
    plt.xlabel('My result')
 
    salvez('demo_vizual.png', rezultat)
    plt.show()

def pas_1a(nume_imagine='castel.jpg'):
    # PASUL 1!!!!!!!
    # imaginea cu castel 
    # imaginea initiala, imaginea redimensionata la o imagine cu 50 de pixeli mai putini in latime folosind algoritmul de pastrare al continutului
    # imaginea initiala redimensionata la o imagine cu 50 de pixeli mai putini in latime cu algoritmul de redimensionare uzuala cu resize din OpenCV
    # testez pe imaginea cu castelul eliminand 50, 75 si 100 de pixeli in latime

    scurt = os.path.splitext(nume_imagine)[0]
    print('PASUL 1!!! a) miscorare pe latime pe imaginea %s' % nume_imagine)

    for n in [50, 75, 100]:
        p = parametri(nume_imagine, resize_option='micsoreazaLatime', num_pixels_width=n)
        rezultat = resize_image(p)
        salvez('%s_latime_%d.png' % (scurt, n), rezultat)
        salvez_varianta_opencv('%s_latime_%d' % (scurt, n), p, rezultat)

def pas_1a_metode(nume_imagine='castel.jpg'):
    scurt = os.path.splitext(nume_imagine)[0]
    print('comparatie intre metodele de alegere a drumului pe %s' % nume_imagine)
 
    for metoda in ['aleator', 'greedy', 'programareDinamica']:
        p = parametri(nume_imagine, resize_option='micsoreazaLatime',
                      num_pixels_width=50, method_select_path=metoda)
        salvez('%s_metoda_%s.png' % (scurt, metoda), resize_image(p))

def pasul_1b(nume_imagine='praga.jpg'):
    scurt = os.path.splitext(nume_imagine)[0]
    print('PASUL 2!!! b) micsorare pe inaltime pe %s' % nume_imagine)
 
    for n in [50, 75, 100]:
        p = parametri(nume_imagine, resize_option='micsoreazaInaltime', num_pixel_height=n)
        rezultat = resize_image(p)
        salvez('%s_inaltime_%d.png' % (scurt, n), rezultat)
        salvez_varianta_opencv('%s_inaltime_%d' % (scurt, n), p, rezultat)

def pasul_1c(nume_imagine):
    scurt = os.path.splitext(nume_imagine)[0]
    print('PASII 1 SI 2!!! c) latime si inaltime pe %s' % nume_imagine)
 
    p = parametri(nume_imagine, resize_option='micsoreazaLatime', num_pixels_width=75)
    rezultat = resize_image(p)
    salvez('%s_c_latime_75.png' % scurt, rezultat)
    salvez_varianta_opencv('%s_c_latime_75' % scurt, p, rezultat)
 
    p = parametri(nume_imagine, resize_option='micsoreazaInaltime', num_pixel_height=75)
    rezultat = resize_image(p)
    salvez('%s_c_inaltime_75.png' % scurt, rezultat)
    salvez_varianta_opencv('%s_c_inaltime_75' % scurt, p, rezultat)

def pasul_3a(nume_imagine='arcTriumf.jpg'):
    scurt = os.path.splitext(nume_imagine)[0]
    print('PASUL 3!!! a) amplificarea continutului pe %s' % nume_imagine)
 
    for f in [1.05, 1.1, 1.2, 1.3]:
        p = parametri(nume_imagine, resize_option='amplificaContinut', factor_amplification=f)
        salvez('%s_amplificat_%.2f.png' % (scurt, f), resize_image(p))

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

def pasul_4b(nume_imagine='lac.jpg'):
    print('PASUL 4!!! b) stergerea unui obiect din %s' % nume_imagine)
    sterg_obiecte(nume_imagine, nr_incercari=5)

def pasul_34c(nume_imagine):
    scurt = os.path.splitext(nume_imagine)[0]
    print('PASII 3-4!! c) amplificare si stergere de obiect pe %s' % nume_imagine)
 
    p = parametri(nume_imagine, resize_option='amplificaContinut', factor_amplification=1.2)
    salvez('%s_c_amplificat_1.20.png' % scurt, resize_image(p))
 
    sterg_obiecte(nume_imagine, nr_incercari=3)

def cer_nume_imagine():
    nume = input('   numele imaginii din %s (ex: poza.jpg): ' % DIRECTOR_DATE).strip()
    if not nume:
        print('   nu ai scris nimic.')
        return None
    if not os.path.exists(os.path.join(DIRECTOR_DATE, nume)):
        print('   nu gasesc %s in %s' % (nume, DIRECTOR_DATE))
        return None
    return nume
 
 
def pasul_1c_interactiv():
    nume = cer_nume_imagine()
    if nume:
        pasul_1c(nume)
 
 
def pasul_34c_interactiv():
    nume = cer_nume_imagine()
    if nume:
        pasul_34c(nume)
 

def ruleaza_tot():
    pas_1a()
    pas_1a_metode()
    pasul_1b()
    pasul_3a()
 
 
OPTIUNI = {
    '1': ('Pasul 1 (a)   castel.jpg, 50/75/100 pixeli in latime', pas_1a),
    '2': ('Pasul 1       comparatie aleator / greedy / programareDinamica', pas_1a_metode),
    '3': ('Pasul 2 (b)   praga.jpg, 50/75/100 pixeli in inaltime', pasul_1b),
    '4': ('Pasii 1-2 (c) latime + inaltime pe o imagine aleasa de mine', pasul_1c_interactiv),
    '5': ('Pasul 3 (a)   arcTriumf.jpg, factori 1.05 / 1.1 / 1.2 / 1.3', pasul_3a),
    '6': ('Pasul 4 (b)   lac.jpg, sterg un obiect selectat cu mouse-ul', pasul_4b),
    '7': ('Pasii 3-4 (c) amplificare + stergere pe o imagine aleasa de mine', pasul_34c_interactiv),
    '8': ('Demo vizual   o singura rulare afisata cu matplotlib', demo_vizual),
    '9': ('Ruleaza TOT   (fara pasii care cer selectie cu mouse-ul)', ruleaza_tot),
}
 
 
def afisez_meniu():
    print('\n' + '=' * 64)
    print('  PROIECT SEAM CARVING - ce vreau sa rulez?')
    print('=' * 64)
    for cheie in sorted(OPTIUNI):
        print('  %s. %s' % (cheie, OPTIUNI[cheie][0]))
    print('  t. Comut afisarea drumurilor (acum: %s)' % ('PORNITA' if SHOW_PATH else 'oprita'))
    print('  0. Iesire')
    print('=' * 64)
 
 
def meniu():
    global SHOW_PATH
 
    # pot da optiunea direct din linia de comanda: python run_project.py 3
    if len(sys.argv) > 1:
        alegere = sys.argv[1]
        if alegere in OPTIUNI:
            OPTIUNI[alegere][1]()
        else:
            print('optiunea %s nu exista' % alegere)
        return
 
    while True:
        afisez_meniu()
        alegere = input('  alegerea mea: ').strip().lower()
 
        if alegere == '0':
            print('  gata.')
            break
        elif alegere == 't':
            SHOW_PATH = not SHOW_PATH
        elif alegere in OPTIUNI:
            OPTIUNI[alegere][1]()
            print('\n  gata, rezultatele sunt in %s' % DIRECTOR_IESIRE)
        else:
            print('  optiune invalida.')
 
 
if __name__ == '__main__':
    meniu()