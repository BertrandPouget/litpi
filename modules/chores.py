import streamlit as st
import pandas as pd
from datetime import datetime

WORKSHEET_NAME = "Chores"
HISTORY_ROWS_TO_SHOW = 10

def _display_ranking(df_scores, fighters):
    """
    Calcola e visualizza la classifica dei punti per le pulizie.
    Assegna medaglie per le prime tre posizioni, gestendo i pareggi.
    """
    st.markdown("### Classifica")
    points = df_scores.copy()
    # Moltiplica le occorrenze di ogni compito per il suo valore in punti
    points[fighters] = points[fighters].multiply(df_scores['Valore'], axis=0)
    rank = points[fighters].sum().sort_values(ascending=False)

    prev_score = -1
    rank_num = 0
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for person, score in rank.items():
        if score != prev_score:
            rank_num += 1
        prev_score = score
        medal = medals.get(rank_num, "")
        st.markdown(f"{medal} **{person}** - *{score:.0f} punti*")

def _display_history(df_history):
    """Visualizza lo storico delle pulizie recenti."""
    st.markdown("### Storico")
    # Itera sulle righe dello storico e le mostra in modo formattato
    for _, row in df_history.head(HISTORY_ROWS_TO_SHOW).iterrows():
        st.markdown(f"""- {row['Quando']}  
        **{row['Persona']}** si è segnato **{row['Cosa']}**""")

def _display_full_table(df_chores):
    """Visualizza la tabella completa delle pulizie con uno stile personalizzato."""
    st.markdown("### Tabella Completa")
    df_chores_style = df_chores.style \
        .applymap(lambda x: 'background-color: #fdf1d6', subset=df_chores.columns[0:2]) \
        .format(precision=0, thousands="'", decimal=".")
    st.dataframe(df_chores_style, use_container_width=True)

def render(conn, fighter, fighters):
    """
    Funzione principale per renderizzare la pagina delle pulizie.
    
    Args:
        conn: La connessione a Google Sheets (GSheetsConnection).
        fighter (str): Il nome dell'utente attualmente selezionato.
        fighters (list): La lista di tutti gli utenti.
    """
    # 1. LETTURA DATI
    # Legge l'intero foglio di lavoro, ricaricando i dati ogni secondo per freschezza.
    df_chores_all = conn.read(worksheet=WORKSHEET_NAME, ttl=1)
    
    # Separa i dati in due DataFrame: uno per i punteggi e uno per lo storico.
    df_chores = df_chores_all[['Compito', 'Valore', 'Andrea', 'Marco', 'Martino']].head(15).copy()
    df_chores_history = df_chores_all[['Persona', 'Quando', 'Cosa']].dropna(axis=0, how='all').copy()

    # 2. VISUALIZZAZIONE
    _display_ranking(df_chores, fighters)
    st.divider()

    # 3. AGGIORNAMENTO
    st.markdown("### Aggiornamento")
    chores_done = st.multiselect(
        label="Seleziona i compiti che hai fatto",
        options=df_chores["Compito"].tolist(),
        default=None
    )

    if st.button("Conferma"):
        with st.spinner(f"Aggiornamento dei lavori di {fighter} in corso..."):
            # Aggiorna il conteggio dei compiti per l'utente
            for chore in chores_done:
                df_chores.loc[df_chores['Compito'] == chore, fighter] += 1
            
            # Crea un nuovo record per lo storico
            new_history_entry = pd.DataFrame([{
                'Persona': fighter,
                'Quando': datetime.now().strftime("%d/%m/%Y, %H:%M"),
                'Cosa': ', '.join(chores_done)
            }])
            
            # Concatena il nuovo record in cima allo storico esistente
            updated_history = pd.concat([new_history_entry, df_chores_history], ignore_index=True)
            
            # Ricostruisce il DataFrame completo per l'aggiornamento del foglio Google
            # NOTA: Manteniamo la struttura originale con una colonna vuota di separazione
            df_to_update = pd.concat([df_chores, pd.DataFrame(columns=[""]), updated_history], axis=1)
            
            conn.update(worksheet=WORKSHEET_NAME, data=df_to_update)
            st.rerun()

    st.divider()
    _display_history(df_chores_history)
    st.divider()
    _display_full_table(df_chores)