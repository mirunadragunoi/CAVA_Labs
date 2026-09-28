# aici pun constantele si caile

import os 

# radacina arhivei cu date 
DIR_DATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tema1')

DIR_ANTRENARE = os.path.join(DIR_DATE, 'antrenare')
DIR_TESTARE = os.path.join(DIR_DATE, 'testare')
DIR_AUXILIARE = os.path.join(DIR_DATE, 'imagini_auxiliare')

# imaginea cu tabla goala, de care am nevouie ca referinta pt mutarea 1
# pt celelalte mutari o sa compar cu imaginea mutarii precedente, doar ca mutarea 1 nu are precedenta

IMAGINE_TABLA_GOALA = os.path.join(DIR_AUXILIARE, '01.jpg')

DIR_REZULTATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rezultate')


# pt tabla
N = 14    # tabla e grila de 14 pe 14
CELULA = 100    # cati pixeli trebuie sa aloc unei celule din imaginea indreptata
DIM = N * CELULA    # dimensiunea imaginii indreptate, in pixeli   


# la detectia tablei lucrez pe marginea micsorata 
# e de 16 ori mai putini pixeli iar tabla e un obiect mai mare, asa ca nu mai pierd din precizie
SCALA_DETECTIE = 0.25 


# cat tai din fiecare imagine de celula inainte sa masor
# fara asta inseamna ca in medie ar intra si linia despartitoare dintre celule si marginea piesei vecine, care se schimba si ea de la o mutare la alta 
MARGINE_CELULA = 18