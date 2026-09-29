import os
import glob


def citeste_pozitie(cale):

    with open(cale, 'rt') as f:
        return f.read().split()[0]


def evalueaza_joc(rezultate, director_adnotari, verbose=True):
    # rezultate = lista de (nume, pozitie, i, j) intoarsa de proceseaza_joc
    corecte = 0
    total = 0
    gresite = []

    for nume, pozitie, _, _ in rezultate:

        cale_gt = os.path.join(director_adnotari, nume + '.txt')

        if not os.path.exists(cale_gt):
            continue

        adevar = citeste_pozitie(cale_gt)
        total += 1

        if pozitie == adevar:
            corecte += 1
        else:
            gresite.append((nume, pozitie, adevar))

    if verbose:

        if total == 0:
            print('   nu am gasit adnotari in %s' % director_adnotari)
        else:
            print('   %d/%d corecte (%.1f%%), %.3f puncte' % (corecte, total, 100.0 * corecte / total, 0.025 * corecte))

            for nume, prezis, adevar in gresite:
                print('      %s: prezis %-4s adevar %-4s' % (nume, prezis, adevar))

    return corecte, total, gresite


def evalueaza_tot(toate_rezultatele, director_adnotari, verbose=True):

    corecte = total = 0

    for joc in sorted(toate_rezultatele):
        if verbose:
            print('jocul %d:' % joc)

        c, t, _ = evalueaza_joc(toate_rezultatele[joc], director_adnotari, verbose)
        corecte += c
        total += t

    if total:
        print('\nTASK 1 TOTAL: %d/%d corecte (%.1f%%)  ->  %.3f puncte din 5' % (corecte, total, 100.0 * corecte / total, 0.025 * corecte))
        
    return corecte, total