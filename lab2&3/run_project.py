"""
    PROIECT MOZAIC
"""

# Parametrii algoritmului sunt definiti in clasa Parameters.
from parameters import *
from build_mosaic import *

# numele imaginii care va fi transformata in mozaic
image_path = './data/imaginiTest/ferrari.jpeg'
params = Parameters(image_path)

# directorul cu imagini folosite pentru realizarea mozaicului
params.small_images_dir = './data/colectie/'
# tipul imaginilor din director
params.image_type = 'png'
# numarul de piese ale mozaicului pe orizontala
# pe verticala vor fi calcultate dinamic a.i sa se pastreze raportul
params.num_pieces_horizontal = 100
# afiseaza piesele de mozaic dupa citirea lor
params.show_small_images = False
# modul de aranjarea a pieselor mozaicului
# optiuni: 'aleator', 'caroiaj'
params.layout = 'caroiaj'
# criteriul dupa care se realizeaza mozaicul
# optiuni: 'aleator', 'distantaCuloareMedie'
params.criterion = 'aleator'
# daca params.layout == 'caroiaj', sa se foloseasca piese hexagonale
params.hexagon = False

# optional ca sa nu pun doua piese identice una langa alta
params.different_neighbors = False


img_mosaic = build_mosaic(params)

cv.imwrite('mozaic.png', img_mosaic)
 
inaltime_afisare = 700
scala = inaltime_afisare / img_mosaic.shape[0]
img_afisat = cv.resize(img_mosaic, None, fx=scala, fy=scala)
cv.imshow('mozaic', img_afisat)
cv.waitKey(0)
cv.destroyAllWindows()

def rulare_experimente(director_imagini='./data/imaginiTest/', director_iesire='./rezultate/'):
    os.makedirs(director_iesire, exist_ok=True)
 
    for nume_imagine in sorted(os.listdir(director_imagini)):
        if not nume_imagine.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        nume_scurt = os.path.splitext(nume_imagine)[0]
 
        # b) caroiaj dreptunghiular, criteriul culorii medii, 4 rezolutii
        for nph in [100, 75, 50, 25]:
            p = Parameters(os.path.join(director_imagini, nume_imagine))
            p.small_images_dir = './data/colectie/'
            p.image_type = 'png'
            p.num_pieces_horizontal = nph
            p.layout = 'caroiaj'
            p.criterion = 'distantaCuloareMedie'
            p.hexagon = False
            cv.imwrite(os.path.join(director_iesire, '%s_caroiaj_%d.png' % (nume_scurt, nph)), build_mosaic(p))
 
        # a) acelasi caroiaj, dar cu criteriul aleator
        p = Parameters(os.path.join(director_imagini, nume_imagine))
        p.small_images_dir = './data/colectie/'
        p.image_type = 'png'
        p.num_pieces_horizontal = 100
        p.layout = 'caroiaj'
        p.criterion = 'aleator'
        p.hexagon = False
        cv.imwrite(os.path.join(director_iesire, '%s_caroiaj_aleator.png' % nume_scurt), build_mosaic(p))
 
        # c) aranjare aleatoare, cu suprapuneri
        p = Parameters(os.path.join(director_imagini, nume_imagine))
        p.small_images_dir = './data/colectie/'
        p.image_type = 'png'
        p.num_pieces_horizontal = 100
        p.layout = 'aleator'
        p.criterion = 'distantaCuloareMedie'
        cv.imwrite(os.path.join(director_iesire, '%s_aleator.png' % nume_scurt), build_mosaic(p))
 
        # piese hexagonale, 4 rezolutii
        for nph in [100, 75, 50, 25]:
            p = Parameters(os.path.join(director_imagini, nume_imagine))
            p.small_images_dir = './data/colectie/'
            p.image_type = 'png'
            p.num_pieces_horizontal = nph
            p.layout = 'caroiaj'
            p.criterion = 'distantaCuloareMedie'
            p.hexagon = True
            cv.imwrite(os.path.join(director_iesire, '%s_hexagon_%d.png' % (nume_scurt, nph)), build_mosaic(p))
 
        print('gata: %s' % nume_imagine)

rulare_experimente()