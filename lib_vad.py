from scipy.fftpack import fft
import numpy as np

# petla obliczenia mocy sygnalu w okanach
def vec_pow(sygnal, winlen):
    pow_vec = np.ones(len(sygnal))
    for cnt in range(0, len(sygnal), winlen):
        tempsamp = sygnal[cnt:cnt + winlen]
        pow_vec[cnt:cnt + winlen] *= np.mean(np.abs(fft(tempsamp)))
    return pow_vec

# wyroznienie fragmentow sygnalu ktorych moc widmowa przekracza wyznaczony prog
def wstepne_zazn(pow_vec, prog=1, stan_wysoki=1):
    wektor_zazn = np.zeros(len(pow_vec))
    for cnt in range(0, len(wektor_zazn)):
        if pow_vec[cnt] > prog:
            wektor_zazn[cnt] = stan_wysoki
    return wektor_zazn

def usun_krotkie(wektor_zazn, stan_wysoki, Fs):
    # wsp. przeliczenia podanego czasu w ms na ilosc probek
    wsp = int(Fs/1000)
    # licznik aktywnosci sygnalu
    znak = 0
    # petla wyciecia impulsow krotszych niz 100 ms ktore nie sasiaduja z zadnym innym sygnalem
    for cnt in range(0, len(wektor_zazn)):
        if stan_wysoki == wektor_zazn[cnt] and stan_wysoki != wektor_zazn[cnt - 1]:
            znak += 1
        elif stan_wysoki == wektor_zazn[cnt] and znak > 0:
            znak += 1
        elif stan_wysoki == wektor_zazn[cnt - 1] and stan_wysoki != wektor_zazn[cnt]:
            if znak < wsp * 100 and not any(wektor_zazn[cnt + 1:cnt + wsp * 400 + 1]) and not any(
                    wektor_zazn[cnt - znak - wsp * 400:cnt - znak - 1]):
                wektor_zazn[cnt - znak:cnt] = 0
            znak = 0

    return wektor_zazn


# petla zaznaczenia 300 ms aktywnosci przed i po sygnale,
# jesli moc fragmentu sygnalu przekracza polowe progu.
def warunkowe_zazn(wektor_zazn, pow_vec, Fs, stan_wysoki=1, poczatek=0, koniec=-1):
    # wsp. przeliczenia podanego czasu w ms na ilosc probek
    wsp = int(Fs/1000)
    cnt = poczatek
    while cnt < koniec:
        if stan_wysoki == wektor_zazn[cnt] and stan_wysoki != wektor_zazn[cnt - 1] and any(
                stan_wysoki / 2 < pow_vec[cnt - 300 * wsp:cnt]):
            wektor_zazn[cnt - 300 * wsp:cnt] = stan_wysoki
        elif stan_wysoki == wektor_zazn[cnt - 1] and stan_wysoki != wektor_zazn[cnt] and any(
                stan_wysoki / 2 < pow_vec[cnt:cnt + 300 * wsp]):
            wektor_zazn[cnt:cnt + 300 * wsp] = stan_wysoki
            cnt += 300 * wsp
        cnt += 1

    return wektor_zazn

# petla zaznaczenia 200 ms aktywnosci przed i po sygnale
def dodatkowe_zazn(wektor_zazn, Fs, stan_wysoki=1,poczatek=0, koniec=-1):
    # wsp. przeliczenia podanego czasu w ms na ilosc probek
    wsp = int(Fs/1000)
    cnt = poczatek
    while cnt < koniec:
        if stan_wysoki == wektor_zazn[cnt] and stan_wysoki != wektor_zazn[cnt - 1] and cnt > 200 * wsp:
            wektor_zazn[cnt - 200 * wsp:cnt] = stan_wysoki
        elif stan_wysoki == wektor_zazn[cnt - 1] and stan_wysoki != wektor_zazn[cnt] and len(
                wektor_zazn) - cnt > 300 * wsp:
            wektor_zazn[cnt:cnt + 200 * wsp] = stan_wysoki
            cnt += 200 * wsp + 2
        cnt += 1
    return wektor_zazn

# ekstrakcja wykrytego sygnalu mowy
def ekstrakcja(sygnal, wektor_zazn, stan_wysoki):
    wyniki = np.zeros((20, 2))
    cnt1 = 0
    cnt2 = 0
    while cnt1 < (len(sygnal) - 8000):
        if stan_wysoki == wektor_zazn[cnt1] and stan_wysoki != wektor_zazn[cnt1 - 1] and cnt1 < 8000:
            wyniki[cnt2, 0] = cnt1
            wyniki[cnt2, 1] += 1
            cnt1 += 1
        elif stan_wysoki == wektor_zazn[cnt1] and stan_wysoki == wektor_zazn[cnt1 - 1] and 4000 < cnt1 < 16000:
            wyniki[cnt2, 1] += 1
            cnt1 += 1
        elif stan_wysoki != wektor_zazn[cnt1] and stan_wysoki == wektor_zazn[cnt1 - 1]:
            cnt2 += 1
            cnt1 += 1
        else:
            cnt1 += 1

        z = np.argmax(wyniki[:,1])

    return sygnal[int(wyniki[z,0]):int(wyniki[z,0])+int(wyniki[z,1])]