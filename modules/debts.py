import streamlit as st
import pandas as pd
from datetime import datetime

WORKSHEET_NAME = "Debts"
HISTORY_ROWS_TO_SHOW = 10

def _display_balances(df_debts, fighters):
    """Visualizza i saldi di ogni persona usando la logica originale per la colorazione."""
    st.markdown("### Saldi")
    debts = df_debts['Bilancio'].tolist()
    for person, debt in zip(fighters, debts):
        # Ripristinata la logica originale che usa il delta per la colorazione
        st.metric(
            label='ciao', 
            value=person, 
            delta=str(round(debt, 2)) + '€', 
            label_visibility='collapsed'
        )

def _display_history(df_history, fighters):
    """Visualizza lo storico delle transazioni."""
    st.markdown("### Storico")
    
    creditors = df_history['Creditore'].tolist()
    transactions = df_history['Soldi'].tolist()
    debtors_str = df_history['Debitori'].tolist()
    days = df_history['Data'].tolist()
    reasons = df_history['Causale'].tolist()
    
    for i in range(min(len(creditors), HISTORY_ROWS_TO_SHOW)):
        debtor = debtors_str[i]
        # Ripristinata la logica originale per la visualizzazione di "Tutti"
        if debtor.find("Andrea") != -1 and debtor.find("Marco") != -1 and debtor.find("Martino") != -1:
            debtor = "Tutti"
            
        st.markdown(
            f"""- {days[i]}: **{float(transactions[i]):.2f}€** per *{reasons[i]}* Pagato da <span style="color:green">**{creditors[i]}**</span> per <span style="color:red">**{debtor}**</span>""",
            unsafe_allow_html=True
        )

def render(conn, fighter, fighters):
    """Funzione principale per renderizzare la pagina dei debiti e crediti."""
    # 1. LETTURA DATI
    df_debts_all = conn.read(worksheet=WORKSHEET_NAME, ttl=1)
    
    df_debts = df_debts_all.iloc[0:3, 0:2].copy()
    df_debts['Bilancio'] = pd.to_numeric(df_debts['Bilancio'])
    df_debts_history = df_debts_all[['Creditore', 'Soldi', 'Debitori', 'Data', 'Causale']] \
        .dropna(axis=0, subset=["Creditore"]).copy()

    # 2. VISUALIZZAZIONE
    _display_balances(df_debts, fighters)

    # 3. AGGIORNAMENTO
    st.markdown("### Aggiornamento")
    credit = st.number_input(label="Quanto hai pagato?", step=1.00)
    debtors = st.multiselect(
        label="Per chi hai pagato?",
        options=fighters,
        default=None
    )
    reason = st.text_input(label="Causale?", placeholder="Causale")

    if st.button("Aggiorna debiti"):
        if not debtors or not reason or credit == 0:
            st.warning("Per favore, compila tutti i campi (importo, beneficiari e causale).")
        else:
            progress_message = st.text(f"Aggiornamento dei crediti di {fighter} in corso...")
            debit = -credit / len(debtors)
            new_df_debts = df_debts.copy()
            new_df_debts.loc[new_df_debts['Persona'] == fighter, 'Bilancio'] += credit
            for debtor_person in debtors:
                new_df_debts.loc[new_df_debts['Persona'] == debtor_person, 'Bilancio'] += debit

            new_df_debts_history = df_debts_history.copy()
            new_history_entry = pd.DataFrame([[fighter, credit, ', '.join(debtors), datetime.now().strftime("%d/%m/%Y, %H:%M"), reason]], columns=new_df_debts_history.columns)
            new_df_debts_history = pd.concat([new_history_entry, new_df_debts_history], ignore_index=True)
            
            new_df_debts_all = pd.concat([new_df_debts, pd.DataFrame([[""]], columns=[""]), new_df_debts_history], axis=1)
            conn.update(worksheet=WORKSHEET_NAME, data=new_df_debts_all)
            st.rerun()
    
    st.markdown("### Storico")
    _display_history(df_debts_history, fighters)