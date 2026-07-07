#--------------------
# Parametri Generali
#--------------------

ETTARI_PER_COLTURA = 100
COLTURE = ["mais", "girasole", "soia"]

#---------------------
# FASE 1 --> RACCOLTA
#---------------------

# --- fissi ---
ORE_LAVORO_GIORNALIERE_RACCOLTA = 10  # ore/giorno

# --- variabili ---

SCENARI_RESA_RACCOLTA = {         # Resa in tonnellate per ettaro (t/ha)
    "mais":     {"scarsa": 9.0,  "media": 10.5, "ottima": 12.0},
    "girasole": {"scarsa": 2.2,  "media": 3.0,  "ottima": 3.5},
    "soia":     {"scarsa": 3.0,  "media": 4.0,  "ottima": 4.5},
}

ETTARI_ORA_MIETITREBBIA = {  # Capacità di raccolta della mietitrebbia (ha/h)
    "standard":  2.0,    # usando 1 mietitrebbia
    "intensiva": 4.0,    # usando 2 mietitrebbie
}

#---------------------
# FASE 2 --> PULIZIA
#---------------------

# --- fissi ---

CAPACITA_ORARIA_PULIZIA = 50.0          # t/h
ORE_LAVORO_GIORNALIERE_PULIZIA = 12     # ore/giorno

# --- variabili ---

RANGE_PERDITA_PULIZIA_PERCENTUALE = {     # Perdita percentuale durante la pulizia (%)
    "mais":     (1.0, 5.0),    # min 1% - max 5%
    "girasole": (2.0, 7.0),    # min 2% - max 7%
    "soia":     (1.0, 4.0),    # min 1% - max 4%
}

#------------------------
# FASE 3 --> ESSICCAZIONE
#------------------------

# --- fissi ---

CAPACITA_ORARIA_ESSICAZIONE = 35.0             # t/h
ORE_LAVORO_GIORNALIERE_ESSICCAZIONE = 12       # ore/giorno

UMIDITA_TARGET = {      # Umidità target da raggiungere dopo l'essiccazione (%)
    "mais":     14.0,
    "girasole": 10.0,
    "soia":     13.0,
}

VELOCITA_RIMOZIONE_UMIDITA = {    # Velocità di rimozione dell'umidità da parte dell'essiccatore (%/h)
    "mais":     5.0,
    "girasole": 4.0,
    "soia":     3.0,
}

# --- variabili ---

UMIDITA_INIZIALE = {    # Umidità del prodotto al momento della raccolta (%)
    "mais":     {"secca": 23.0, "umida": 30.0},
    "girasole": {"secca":  9.0, "umida": 18.0},
    "soia":     {"secca": 18.0, "umida": 25.0},
}

#------------------------
# FASE 4 --> STOCCAGGIO
#------------------------

# --- fissi ---

CAPIENZA_SILOS = {    # Capienza massima dei silos per coltura (t)
    "mais":     1200.0,
    "girasole":  600.0,
    "soia":      600.0,
}

PERDITA_STOCCAGGIO = 0.01    # perdita fissa durante lo stoccaggio (1%)

#----------------------------------
# FASE 5 --> DIVISIONE LINEE A e B
#----------------------------------

# --- variabili ---

RANGE_LINEA_A_PERCENTUALE = {    # Percentuale del prodotto destinata alla Linea A - confezionamento diretto (%)
    "mais":     (40.0, 60.0),    # min 40% - max 60%
    "girasole": (40.0, 50.0),    # min 40% - max 50%
    "soia":     (20.0, 30.0),    # min 20% - max 30%
}                                # La percentuale restante va automaticamente alla Linea B - macinazione

#----------------------------
# FASE 6 --> CONFEZIONAMENTO
#----------------------------

# --- fissi ---

CAPACITA_ORARIA_CONFEZIONAMENTO = 15.0         # Capacità dell'impianto di confezionamento (t/h)
ORE_LAVORO_GIORNALIERE_CONFEZIONAMENTO = 12    # Ore di lavoro giornaliere dell'impianto di confezionamento (h/giorno)
PESO_SACCO_KG = 25                             # Peso di ogni sacco confezionato (kg)

#------------------------------------------------------
# FASE 7 --> TOSTATURA (solo per la soia nella linea B)
#------------------------------------------------------

# --- fissi ---

CAPACITA_ORARIA_TOSTATURA = 20.0        # Capacità dell'impianto di tostatura (t/h)
ORE_LAVORO_GIORNALIERE_TOSTATURA = 12   # Ore di lavoro giornaliere dell'impianto di tostatura (h/giorno)
PERDITA_TOSTATURA = 0.015               # Perdita fissa durante la tostatura (1.5%)

#------------------------------------------------------------------------
# FASE 8 --> MACINAZIONE ( per tutte le colture della linea produttiva B)
#-------------------------------------------------------------------------

# --- fissi ---

CAPACITA_ORARIA_MACINAZIONE = 15.0        # Capacità dell'impianto di macinazione (t/h)
ORE_LAVORO_GIORNALIERE_MACINAZIONE = 12   # Ore di lavoro giornaliere dell'impianto di macinazione(h/giorno)

RESA_MACINAZIONE = {     # Resa della macinazione per coltura - quantità di farina ottenuta per tonnellata (%)
    "mais":     0.96,    # 96% diventa farina - 4% scarti
    "girasole": 0.93,    # 93% diventa farina - 7% scarti
    "soia":     0.90,    # 90% diventa farina - 10% scarti
}

#-------------------
# PRODOTTI FINALI
#-------------------

NOMI_PRODOTTI = {      # Nomi dei prodotti finali per linea e coltura
    "mais_A":     "Chicchi di Mais Confezionati",       # Linea A
    "mais_B":     "Farina di Mais",                     # Linea B
    "girasole_A": "Semi di Girasole Confezionati",      # Linea A
    "girasole_B": "Farina di Girasole",                 # Linea B
    "soia_A":     "Granella di Soia Confezionata",      # Linea A
    "soia_B":     "Farina di Soia Tostata",             # Linea B
}