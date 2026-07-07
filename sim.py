import math
import random
from collections import deque

from constants import *

class ImpiantoFIFO:
    def __init__(self):
        self.tempo_liberazione = 0.0

    def processa(self, lotti):
        lotti_ordinati = sorted(lotti, key=lambda x: x["t_arrivo"])
        coda = deque(lotti_ordinati)
        esiti = {}
        
        while coda:
            lotto = coda.popleft()
            coltura = lotto["coltura"]
            t_arrivo = lotto["t_arrivo"]
            durata_ore = lotto["durata_ore"]

            if durata_ore == 0:
                t_inizio = t_arrivo
                t_fine = t_arrivo
                t_attesa = 0.0
            else:
                t_inizio = max(t_arrivo, self.tempo_liberazione)
                t_attesa = t_inizio - t_arrivo
                t_fine = t_inizio + durata_ore
                self.tempo_liberazione = t_fine

            esiti[coltura] = {
                "t_inizio": round(t_inizio, 2),
                "t_attesa": round(t_attesa, 2),
                "t_fine": round(t_fine, 2)
            }
        return esiti

def genera_quantita():
    quantita = {}
    for coltura in COLTURE:
        tetto_min = SCENARI_RESA_RACCOLTA[coltura]["scarsa"] * ETTARI_PER_COLTURA
        tetto_max = min(SCENARI_RESA_RACCOLTA[coltura]["ottima"] * ETTARI_PER_COLTURA, CAPIENZA_SILOS[coltura])
        quantita[coltura] = round(random.uniform(tetto_min, tetto_max), 2)
    return quantita

def scegli_scenario_resa():
    return {coltura: random.choice(["scarsa", "media", "ottima"]) for coltura in COLTURE}

def scegli_intensita_raccolta():
    return random.choice(["standard", "intensiva"])

def scegli_scenario_climatico():
    return random.choice(["secca", "umida"])


def calcola_capacita_raccolta(coltura, scenario_resa, scenario_raccolta):
    """Calcola la capacità di raccolta oraria e giornaliera in base alla coltura,
    alla resa estratta e all'intensità di raccolta (numero di mietitrebbie)"""

    resa_t_ha = SCENARI_RESA_RACCOLTA[coltura][scenario_resa]
    ha_h = ETTARI_ORA_MIETITREBBIA[scenario_raccolta]
    cap_oraria = ha_h * resa_t_ha
    cap_giornaliera = cap_oraria * ORE_LAVORO_GIORNALIERE_RACCOLTA

    return round(cap_oraria, 2), round(cap_giornaliera, 2)


def calcola_tempo_raccolta(quantita, cap_oraria):
    """Calcola il tempo necessario per raccogliere tutta la quantità disponibile"""

    tempo_ore = quantita / cap_oraria
    tempo_giorni = tempo_ore / ORE_LAVORO_GIORNALIERE_RACCOLTA

    return round(tempo_ore, 2), round(tempo_giorni, 2)


def calcola_pulizia(coltura, quantita_in):
    """Calcola la quantità in uscita, la perdita e il tempo necessario per la pulizia
    La perdita percentuale viene estratta casualmente tra il minimo e il massimo previsti per ogni coltura"""

    perdita_minima, perdita_massima = RANGE_PERDITA_PULIZIA_PERCENTUALE[coltura]
    perdita_perc = random.uniform(perdita_minima, perdita_massima) / 100.0
    perdita = round(quantita_in * perdita_perc, 2)
    quantita_out = round(quantita_in - perdita, 2)
    tempo_ore = round(quantita_in / CAPACITA_ORARIA_PULIZIA, 2)
    tempo_giorni = round(tempo_ore / ORE_LAVORO_GIORNALIERE_PULIZIA, 2)

    return quantita_out, perdita, tempo_ore, tempo_giorni


def calcola_essiccazione(coltura, quantita_in, scenario_climatico):
    """Calcola la quantità in uscita, la perdita e il tempo necessario per l'essiccazione
    Se l'umidità iniziale è già sotto il target la fase viene saltata completamente"""

    umidita_iniziale = UMIDITA_INIZIALE[coltura][scenario_climatico]
    umidita_target = UMIDITA_TARGET[coltura]

    if umidita_iniziale <= umidita_target:
        return quantita_in, 0.0, 0.0, 0.0

    delta_umidita = umidita_iniziale - umidita_target
    tempo_umidita = delta_umidita / VELOCITA_RIMOZIONE_UMIDITA[coltura]
    tempo_impianto = quantita_in / CAPACITA_ORARIA_ESSICAZIONE
    tempo_totale_ore = round(tempo_impianto * tempo_umidita, 2)
    tempo_giorni = round(tempo_totale_ore / ORE_LAVORO_GIORNALIERE_ESSICCAZIONE, 2)
    peso_finale = round(quantita_in * (100 - umidita_iniziale) / (100 - umidita_target), 2)
    perdita = round(quantita_in - peso_finale, 2)

    return peso_finale, perdita, tempo_totale_ore, tempo_giorni


def calcola_stoccaggio(quantita_in):
    """Calcola la quantità in uscita e la perdita fissa durante lo stoccaggio"""

    perdita = round(quantita_in * PERDITA_STOCCAGGIO, 2)
    quantita_out = round(quantita_in - perdita, 2)

    return quantita_out, perdita


def calcola_distribuzione_linee(coltura, quantita_in):
    """Divide la quantità in uscita dallo stoccaggio tra Linea A e Linea B
    La percentuale destinata alla Linea A viene estratta casualmente tra il minimo e il massimo previsti"""

    perc_minima, perc_massima = RANGE_LINEA_A_PERCENTUALE[coltura]
    perc_A = random.uniform(perc_minima, perc_massima) / 100.0
    perc_B = 1.0 - perc_A
    quantita_A = round(quantita_in * perc_A, 2)
    quantita_B = round(quantita_in - quantita_A, 2)

    return quantita_A, quantita_B, round(perc_A * 100, 1), round(perc_B * 100, 1)


def calcola_tostatura(quantita_in):
    """Calcola la quantità in uscita, la perdita e il tempo necessario per la tostatura. Applicata SOLO alla soia nella Linea B"""

    tempo_ore = round(quantita_in / CAPACITA_ORARIA_TOSTATURA, 2)
    tempo_giorni = round(tempo_ore / ORE_LAVORO_GIORNALIERE_TOSTATURA, 2)
    perdita = round(quantita_in * PERDITA_TOSTATURA, 2)
    quantita_out = round(quantita_in - perdita, 2)

    return quantita_out, perdita, tempo_ore, tempo_giorni


def calcola_macinazione(coltura, quantita_in):
    """Calcola la quantità di farina in uscita, la perdita e il tempo necessario per la macinazione
    La resa varia per coltura - la parte restante costituisce gli scarti della macinazione"""

    tempo_ore = round(quantita_in / CAPACITA_ORARIA_MACINAZIONE, 2)
    tempo_giorni = round(tempo_ore / ORE_LAVORO_GIORNALIERE_MACINAZIONE, 2)
    quantita_out = round(quantita_in * RESA_MACINAZIONE[coltura], 2)
    perdita = round(quantita_in - quantita_out, 2)

    return quantita_out, perdita, tempo_ore, tempo_giorni


def calcola_confezionamento(quantita_in):
    """Calcola il numero di sacchi prodotti e il tempo necessario per il confezionamento
    La quantità in ingresso viene convertita da tonnellate a kg"""

    quantita_kg = quantita_in * 1000
    n_sacchi = math.floor(quantita_kg / PESO_SACCO_KG)
    tempo_ore = round(quantita_in / CAPACITA_ORARIA_CONFEZIONAMENTO, 2)
    tempo_giorni = round(tempo_ore / ORE_LAVORO_GIORNALIERE_CONFEZIONAMENTO, 2)
    cap_giornaliera = CAPACITA_ORARIA_CONFEZIONAMENTO * ORE_LAVORO_GIORNALIERE_CONFEZIONAMENTO

    return n_sacchi, tempo_ore, tempo_giorni, cap_giornaliera


def calcola_perdite_totali(r):
    """Somma tutte le perdite di tutte le fasi e colture in un unico valore totale in tonnellate"""

    perdite = 0.0
    for c in COLTURE:
        perdite += r["fasi"][c]["pulizia"]["perdita"]
        perdite += r["fasi"][c]["essiccazione"]["perdita"]
        perdite += r["fasi"][c]["stoccaggio"]["perdita"]
        perdite += r["fasi"][c]["macinazione"]["perdita"]
    perdite += r["fasi"]["soia"]["tostatura"]["perdita"]

    return round(perdite, 2)

def esegui_simulazione(scenario_resa=None, scenario_raccolta=None, scenario_climatico=None):
    scenario_resa = scenario_resa or scegli_scenario_resa()
    scenario_raccolta = scenario_raccolta or scegli_intensita_raccolta()
    scenario_climatico = scenario_climatico or scegli_scenario_climatico()

    quantita_iniziale = genera_quantita()
    risultati_fasi = {c: {} for c in COLTURE}

    imp_pulizia = ImpiantoFIFO()
    imp_essiccazione = ImpiantoFIFO()
    imp_confez_a = ImpiantoFIFO()
    imp_macinazione = ImpiantoFIFO()
    imp_confez_b = ImpiantoFIFO()

    for c in COLTURE:
        cap_oraria, cap_gg = calcola_capacita_raccolta(c, scenario_resa[c], scenario_raccolta)
        t_ore, t_gg = calcola_tempo_raccolta(quantita_iniziale[c], cap_oraria)
        risultati_fasi[c]["raccolta"] = {
            "t_inizio": 0.0,
            "t_fine": round(t_ore, 2),
            "t_attesa": 0.0,
            "tempo_ore": t_ore,
            "tempo_gg": t_gg,
            "cap_oraria": cap_oraria,
            "cap_giornaliera": cap_gg,
            "q_uscita": quantita_iniziale[c],
        }

    lotti_pulizia = []
    dati_pulizia = {}
    for c in COLTURE:
        q_in = risultati_fasi[c]["raccolta"]["q_uscita"]
        q_out, perd, t_ore, t_gg = calcola_pulizia(c, q_in)
        dati_pulizia[c] = {"q_in": q_in, "q_out": q_out, "perdita": perd, "t_ore": t_ore, "t_gg": t_gg}
        lotti_pulizia.append({"coltura": c, "t_arrivo": risultati_fasi[c]["raccolta"]["t_fine"], "durata_ore": t_ore})
    
    esiti_pulizia = imp_pulizia.processa(lotti_pulizia)
    for c in COLTURE:
        risultati_fasi[c]["pulizia"] = {
            "t_arrivo": risultati_fasi[c]["raccolta"]["t_fine"],
            "t_inizio": esiti_pulizia[c]["t_inizio"],
            "t_fine": esiti_pulizia[c]["t_fine"],
            "t_attesa": esiti_pulizia[c]["t_attesa"],
            "tempo_ore": dati_pulizia[c]["t_ore"],
            "tempo_gg": dati_pulizia[c]["t_gg"],
            "q_ingresso": dati_pulizia[c]["q_in"],
            "q_uscita": dati_pulizia[c]["q_out"],
            "perdita": dati_pulizia[c]["perdita"],
        }

    lotti_essiccazione = []
    dati_essiccazione = {}
    for c in COLTURE:
        q_in = risultati_fasi[c]["pulizia"]["q_uscita"]
        q_out, perd, t_ore, t_gg = calcola_essiccazione(c, q_in, scenario_climatico)
        dati_essiccazione[c] = {"q_in": q_in, "q_out": q_out, "perdita": perd, "t_ore": t_ore, "t_gg": t_gg}
        lotti_essiccazione.append({"coltura": c, "t_arrivo": risultati_fasi[c]["pulizia"]["t_fine"], "durata_ore": t_ore})
    
    esiti_essiccazione = imp_essiccazione.processa(lotti_essiccazione)
    for c in COLTURE:
        risultati_fasi[c]["essiccazione"] = {
            "t_arrivo": risultati_fasi[c]["pulizia"]["t_fine"],
            "t_inizio": esiti_essiccazione[c]["t_inizio"],
            "t_fine": esiti_essiccazione[c]["t_fine"],
            "t_attesa": esiti_essiccazione[c]["t_attesa"],
            "tempo_ore": dati_essiccazione[c]["t_ore"],
            "tempo_gg": dati_essiccazione[c]["t_gg"],
            "q_ingresso": dati_essiccazione[c]["q_in"],
            "q_uscita": dati_essiccazione[c]["q_out"],
            "perdita": dati_essiccazione[c]["perdita"],
        }

    for c in COLTURE:
        t_arr = risultati_fasi[c]["essiccazione"]["t_fine"]
        q_in = risultati_fasi[c]["essiccazione"]["q_uscita"]
        q_out, perd = calcola_stoccaggio(q_in)
        
        risultati_fasi[c]["stoccaggio"] = {
            "t_arrivo": round(t_arr, 2),
            "t_fine": round(t_arr, 2),
            "t_attesa": 0.0,
            "q_ingresso": q_in,
            "q_uscita": q_out,
            "perdita": perd,
        }

        q_a, q_b, perc_a, perc_b = calcola_distribuzione_linee(c, q_out)
        risultati_fasi[c]["split"] = {
            "t_fine": round(t_arr, 2),
            "q_A": q_a,
            "q_B": q_b,
            "perc_A": perc_a,
            "perc_B": perc_b,
        }

    lotti_confez_a = []
    dati_confez_a = {}
    for c in COLTURE:
        q_in = risultati_fasi[c]["split"]["q_A"]
        n_sacchi, t_ore, t_gg, cap_gg = calcola_confezionamento(q_in)
        dati_confez_a[c] = {"q_in": q_in, "n_sacchi": n_sacchi, "t_ore": t_ore, "t_gg": t_gg}
        lotti_confez_a.append({"coltura": c, "t_arrivo": risultati_fasi[c]["split"]["t_fine"], "durata_ore": t_ore})
    
    esiti_confez_a = imp_confez_a.processa(lotti_confez_a)
    for c in COLTURE:
        risultati_fasi[c]["confez_A"] = {
            "t_arrivo": risultati_fasi[c]["split"]["t_fine"],
            "t_inizio": esiti_confez_a[c]["t_inizio"],
            "t_fine": esiti_confez_a[c]["t_fine"],
            "t_attesa": esiti_confez_a[c]["t_attesa"],
            "tempo_ore": dati_confez_a[c]["t_ore"],
            "tempo_gg": dati_confez_a[c]["t_gg"],
            "q_ingresso": dati_confez_a[c]["q_in"],
            "n_sacchi": dati_confez_a[c]["n_sacchi"],
        }

    t_arr_soia = risultati_fasi["soia"]["split"]["t_fine"]
    q_in_soia = risultati_fasi["soia"]["split"]["q_B"]
    q_out_soia, perd_soia, t_ore_soia, t_gg_soia = calcola_tostatura(q_in_soia)
    t_fine_soia = t_arr_soia + t_ore_soia

    risultati_fasi["soia"]["tostatura"] = {
        "t_arrivo": round(t_arr_soia, 2),
        "t_inizio": round(t_arr_soia, 2),
        "t_fine": round(t_fine_soia, 2),
        "t_attesa": 0.0,
        "tempo_ore": t_ore_soia,
        "tempo_gg": t_gg_soia,
        "q_ingresso": q_in_soia,
        "q_uscita": q_out_soia,
        "perdita": perd_soia,
    }

    lotti_macinazione = []
    dati_macinazione = {}
    for c in COLTURE:
        if c == "soia":
            q_in = risultati_fasi["soia"]["tostatura"]["q_uscita"]
            t_arr = risultati_fasi["soia"]["tostatura"]["t_fine"]
        else:
            q_in = risultati_fasi[c]["split"]["q_B"]
            t_arr = risultati_fasi[c]["split"]["t_fine"]

        q_out, perd, t_ore, t_gg = calcola_macinazione(c, q_in)
        dati_macinazione[c] = {"q_in": q_in, "q_out": q_out, "perdita": perd, "t_ore": t_ore, "t_gg": t_gg, "t_arr": t_arr}
        lotti_macinazione.append({"coltura": c, "t_arrivo": t_arr, "durata_ore": t_ore})
    
    esiti_macinazione = imp_macinazione.processa(lotti_macinazione)
    for c in COLTURE:
        risultati_fasi[c]["macinazione"] = {
            "t_arrivo": dati_macinazione[c]["t_arr"],
            "t_inizio": esiti_macinazione[c]["t_inizio"],
            "t_fine": esiti_macinazione[c]["t_fine"],
            "t_attesa": esiti_macinazione[c]["t_attesa"],
            "tempo_ore": dati_macinazione[c]["t_ore"],
            "tempo_gg": dati_macinazione[c]["t_gg"],
            "q_ingresso": dati_macinazione[c]["q_in"],
            "q_uscita": dati_macinazione[c]["q_out"],
            "perdita": dati_macinazione[c]["perdita"],
        }

    lotti_confez_b = []
    dati_confez_b = {}
    for c in COLTURE:
        q_in = risultati_fasi[c]["macinazione"]["q_uscita"]
        n_sacchi, t_ore, t_gg, cap_gg = calcola_confezionamento(q_in)
        t_arr = risultati_fasi[c]["macinazione"]["t_fine"]
        
        dati_confez_b[c] = {"q_in": q_in, "n_sacchi": n_sacchi, "t_ore": t_ore, "t_gg": t_gg}
        lotti_confez_b.append({"coltura": c, "t_arrivo": t_arr, "durata_ore": t_ore})
    
    esiti_confez_b = imp_confez_b.processa(lotti_confez_b)
    for c in COLTURE:
        risultati_fasi[c]["confez_B"] = {
            "t_arrivo": risultati_fasi[c]["macinazione"]["t_fine"],
            "t_inizio": esiti_confez_b[c]["t_inizio"],
            "t_fine": esiti_confez_b[c]["t_fine"],
            "t_attesa": esiti_confez_b[c]["t_attesa"],
            "tempo_ore": dati_confez_b[c]["t_ore"],
            "tempo_gg": dati_confez_b[c]["t_gg"],
            "q_ingresso": dati_confez_b[c]["q_in"],
            "n_sacchi": dati_confez_b[c]["n_sacchi"],
        }

    t_totale = max(
        max(risultati_fasi[c]["confez_A"]["t_fine"] for c in COLTURE),
        max(risultati_fasi[c]["confez_B"]["t_fine"] for c in COLTURE),
    )

    return {
        "scenario_resa": scenario_resa,
        "scenario_raccolta": scenario_raccolta,
        "scenario_climatico": scenario_climatico,
        "quantita": quantita_iniziale,
        "fasi": risultati_fasi,
        "t_totale": round(t_totale, 2),
        "t_totale_gg": round(t_totale / ORE_LAVORO_GIORNALIERE_RACCOLTA, 2),
    }

def esegui_simulazioni_multiple(n=1000):
    """Esegue n simulazioni casuali e restituisce tutti i risultati in una lista"""
    risultati = []
    print(f"\n  Avvio di {n} simulazioni...")

    for i in range(n):
        risultati.append(esegui_simulazione())

    print(f"  Completate {len(risultati)} simulazioni!")
    return risultati