import streamlit as st
import random
import statistics
import os
import sim
import export as exp

def mostra_risultati_singola(r):
    perdite_tot = sim.calcola_perdite_totali(r)
    quantita_tot = sum(r["quantita"][c] for c in sim.COLTURE)

    st.subheader("Scenari estratti")
    col1, col2 = st.columns(2)
    col1.write(f"**Scenario raccolta:** {r['scenario_raccolta'].capitalize()}")
    col2.write(f"**Annata climatica:** {r['scenario_climatico'].capitalize()}")
    
    st.write("**Rese per coltura:**")
    for c in sim.COLTURE:
        st.write(f"- {c.capitalize()}: {r['scenario_resa'][c].capitalize()} ({r['quantita'][c]:.2f} t)")

    st.subheader("Riepilogo Finale Lotto di Produzione")
    c1, c2, c3 = st.columns(3)
    c1.metric("Quantità Totale", f"{quantita_tot:.2f} t")
    c2.metric("Perdite Totali", f"{perdite_tot:.2f} t", delta_color="inverse")
    c3.metric("Tempo Totale", f"{r['t_totale']:.2f} h")

def mostra_analisi_risultati(tutti_i_risultati):
    tempi_totali = [r["t_totale"] for r in tutti_i_risultati]
    perdite_totali = [sim.calcola_perdite_totali(r) for r in tutti_i_risultati]

    st.subheader("Statistiche Generali")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("N. Simulazioni", len(tutti_i_risultati))
    c2.metric("Tempo Medio", f"{round(statistics.mean(tempi_totali), 2)} h")
    c3.metric("Tempo Minimo", f"{round(min(tempi_totali), 2)} h")
    c4.metric("Tempo Massimo", f"{round(max(tempi_totali), 2)} h")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Dev. Standard Tempi", f"{round(statistics.stdev(tempi_totali), 2)} h")
    c6.metric("Perdita Media", f"{round(statistics.mean(perdite_totali), 2)} t")
    c7.metric("Perdita Minima", f"{round(min(perdite_totali), 2)} t")
    c8.metric("Perdita Massima", f"{round(max(perdite_totali), 2)} t")

    fasi_da_analizzare = {
        "pulizia": "Pulizia",
        "essiccazione": "Essiccazione",
        "tostatura": "Tostatura (solo Soia)",
        "confez_A": "Confezionamento A",
        "macinazione": "Macinazione",
        "confez_B": "Confezionamento B",
    }

    attesa_media_per_fase = {}
    st.subheader("Attese e Durate Medie per Fase")
    
    dati_tabella = []
    for chiave, nome in fasi_da_analizzare.items():
        attese = []
        durate = []
        for r in tutti_i_risultati:
            if chiave == "tostatura":
                attese.append(r["fasi"]["soia"]["tostatura"]["t_attesa"])
                durate.append(r["fasi"]["soia"]["tostatura"]["tempo_ore"])
            else:
                for c in sim.COLTURE:
                    attese.append(r["fasi"][c][chiave]["t_attesa"])
                    durate.append(r["fasi"][c][chiave]["tempo_ore"])
        
        media_attesa = round(statistics.mean(attese), 2)
        attesa_media_per_fase[nome] = media_attesa
        
        dati_tabella.append({
            "Fase": nome,
            "Attesa Media (h)": media_attesa,
            "Attesa Max (h)": round(max(attese), 2),
            "Durata Media (h)": round(statistics.mean(durate), 2),
            "Durata Max (h)": round(max(durate), 2)
        })

    st.dataframe(dati_tabella, width="stretch")

    collo_di_bottiglia = max(attesa_media_per_fase, key=attesa_media_per_fase.get)
    st.warning(f"**Il collo di bottiglia è:** {collo_di_bottiglia.upper()} (Attesa media: {attesa_media_per_fase[collo_di_bottiglia]} h)")

    st.subheader("Grafici di Analisi")
    figure = exp.crea_figure_analisi(tutti_i_risultati)
    for fig in figure:
        st.pyplot(fig)

def scarica_file_creato(percorso_file, label_pulsante, mime_type):
    if os.path.exists(percorso_file):
        with open(percorso_file, "rb") as f:
            dati = f.read()
        st.download_button(
            label=label_pulsante,
            data=dati,
            file_name=percorso_file,
            mime=mime_type
        )

def main():
    st.set_page_config(page_title="Simulatore Agricolo", layout="wide")

    if "risultati_singola" not in st.session_state:
        st.session_state.risultati_singola = None
    if "risultati_1000" not in st.session_state:
        st.session_state.risultati_1000 = None
    if "risultati_manuale" not in st.session_state:
        st.session_state.risultati_manuale = None
    if "risultati_seed" not in st.session_state:
        st.session_state.risultati_seed = None
        st.session_state.seed_usato = None

    opzioni_menu = [
        "Simulazione singola casuale",
        "1000 simulazioni con analisi statistica",
        "Simulazione con parametri manuali",
        "Simulazione con seed fisso (riproducibile)"
    ]

    scelta = st.sidebar.radio("Menu Principale", opzioni_menu)

    if scelta == opzioni_menu[0]:
        st.header("Simulazione Singola Casuale")
        if st.button("Avvia Simulazione", type="primary"):
            st.session_state.risultati_singola = sim.esegui_simulazione()
            exp.esporta_excel_singola_random(st.session_state.risultati_singola, "simulazione_random.xlsx")
            
        if st.session_state.risultati_singola:
            mostra_risultati_singola(st.session_state.risultati_singola)
            scarica_file_creato("simulazione_random.xlsx", "Scarica Risultati in Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif scelta == opzioni_menu[1]:
        st.header("Analisi Statistica su 1000 Simulazioni")
        if st.button("Avvia 1000 Simulazioni", type="primary"):
            with st.spinner("Esecuzione delle simulazioni in corso. Potrebbe richiedere qualche secondo..."):
                st.session_state.risultati_1000 = sim.esegui_simulazioni_multiple(1000)
                exp.esporta_excel_analisi(st.session_state.risultati_1000, "analisi_1000_simulazioni.xlsx")
                exp.salva_grafici_pdf(st.session_state.risultati_1000, "analisi_grafici.pdf")
                
        if st.session_state.risultati_1000:
            mostra_analisi_risultati(st.session_state.risultati_1000)
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                scarica_file_creato("analisi_1000_simulazioni.xlsx", "Scarica Analisi in Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col_btn2:
                scarica_file_creato("analisi_grafici.pdf", "Scarica Grafici in PDF", "application/pdf")

    elif scelta == opzioni_menu[2]:
        st.header("Simulazione con Parametri Manuali")
        
        col_m1, col_m2 = st.columns(2)
        scenario_raccolta = col_m1.selectbox("Scenario di raccolta (Mietitrebbie)", ["standard", "intensiva"])
        scenario_climatico = col_m2.selectbox("Annata climatica", ["secca", "umida"])
        st.subheader("Resa Colture")
        tipo_resa = st.radio("Impostazione resa", ["Uguale per tutte", "Diversa per ogni coltura"])
        
        scenario_resa = {}
        if tipo_resa == "Uguale per tutte":
            resa_comune = st.selectbox("Seleziona la resa generale", ["scarsa", "media", "ottima"])
            scenario_resa = {c: resa_comune for c in sim.COLTURE}
        else:
            col_c1, col_c2, col_c3 = st.columns(3)
            scenario_resa["mais"] = col_c1.selectbox("Resa Mais", ["scarsa", "media", "ottima"])
            scenario_resa["girasole"] = col_c2.selectbox("Resa Girasole", ["scarsa", "media", "ottima"])
            scenario_resa["soia"] = col_c3.selectbox("Resa Soia", ["scarsa", "media", "ottima"])

        if st.button("Esegui Simulazione Manuale", type="primary"):
            st.session_state.risultati_manuale = sim.esegui_simulazione(
                scenario_resa=scenario_resa,
                scenario_raccolta=scenario_raccolta,
                scenario_climatico=scenario_climatico
            )
            exp.esporta_excel_manuale(st.session_state.risultati_manuale, "simulazione_manuale.xlsx")

        if st.session_state.risultati_manuale:
            mostra_risultati_singola(st.session_state.risultati_manuale)
            scarica_file_creato("simulazione_manuale.xlsx", "Scarica Risultati Manuali in Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif scelta == opzioni_menu[3]:
        st.header("Simulazione con Seed Fisso")
        seed_inserito = st.number_input("Inserisci il seed (numero intero)", value=42, step=1, format="%d")
        
        if st.button("Avvia Simulazione", type="primary"):
            random.seed(int(seed_inserito))
            st.session_state.risultati_seed = sim.esegui_simulazione()
            st.session_state.seed_usato = int(seed_inserito)
            
            nome_file = f"simulazione_seed{st.session_state.seed_usato}.xlsx"
            exp.esporta_excel_seed(st.session_state.risultati_seed, nome_file)

        if st.session_state.risultati_seed:
            mostra_risultati_singola(st.session_state.risultati_seed)
            nome_file_attuale = f"simulazione_seed{st.session_state.seed_usato}.xlsx"
            scarica_file_creato(nome_file_attuale, "Scarica Risultati in Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()