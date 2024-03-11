import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import warnings
warnings.filterwarnings("ignore")

# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df_chores = conn.read(worksheet="Chores", usecols=list(range(0,5)),nrows=14, ttl=1)
df_shopping = conn.read(worksheet="Shopping", usecols=list(range(0,1)), ttl=1)
df_debts = conn.read(worksheet="Debts", usecols=list(range(0,2)), nrows=3, ttl=1)

# Compute points and rank
points = df_chores.copy()
points[['Andrea', 'Martino', 'Marco']] = points[['Andrea', 'Martino', 'Marco']].multiply(df_chores['Valore'], axis=0)
rank = points[['Andrea', 'Martino', 'Marco']].sum().sort_values(ascending=False)

st.title('LitPi :house:\n Streamlit per Casa Lippi')

st.markdown('## Selezione personaggio')
fighter = st.radio(label = "Chi sei?",
        options = ("Andrea", "Marco", "Martino"),
        index = None)

st.markdown('---')

selected = option_menu(
    menu_title = None,
    options = ["Pulizie", "Spesa", 'Debiti'], 
    icons = ['droplet', "list-task", 'piggy-bank'], 
    menu_icon = "cast",
    default_index=0,
    orientation="horizontal")

# 1. Pulizie
if selected == 'Pulizie':
    st.markdown("## Aggiornamento")
    chores = st.multiselect(label = "Seleziona i compiti che hai fatto",
                        options = df_chores.loc[:, "Compito"].tolist(),
                        default = None)

    if st.button("Conferma"):
        progress_message = st.text(f"Aggiornamento dei lavori di {fighter} in corso...")
        new_df_chores = df_chores.copy(deep=True)
        for chore in chores:
            new_df_chores.loc[new_df_chores['Compito'] == chore, fighter] += 1
        conn.update(worksheet="Chores", data=new_df_chores)
        progress_message.text("Aggiornamento completato!\nRicarica la pagina per vedere i risultati.")

    st.markdown("## Classifica")
    for i, (name, score) in enumerate(rank.items(), 1):
        medal = ":first_place_medal:" if i == 1 else ":second_place_medal:" if i == 2 else ":third_place_medal:" if i == 3 else ""
        st.markdown(f"{medal} **{name}** - *{score} punti*")

    st.markdown("## Tabella Completa")
    st.dataframe(df_chores)

# 2. Spesa
if selected == 'Spesa':
    st.markdown("## Lista della spesa")
    shopping_list = df_shopping['Spesa'].dropna().tolist()
    if shopping_list == []:
        st.markdown("La lista della spesa è vuota")
    else:
        for i, item in enumerate(shopping_list):
            st.markdown(f"{i+1}. {item}")

    st.markdown("#### Aggiungi un elemento")
    user_input = st.text_input("Aggiungi un elemento alla lista:")
    if st.button("Aggiungi"):
        progress_message = st.text("Aggiunta elemento...")
        new_df_shopping = df_shopping.copy(deep=True)
        new_df_shopping = pd.concat([pd.DataFrame({'Spesa': [user_input]}), df_shopping], ignore_index=True)
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Elemento aggiunto!\nRicarica la pagina per vedere i risultati.")

    st.markdown("#### Elimina singoli elementi")
    elements_to_delete = st.multiselect(label = "Seleziona gli elementi da eliminare",
                                        options = shopping_list,
                                        default = None)
    
    if st.button("Elimina"):
        progress_message = st.text("Eliminazione elementi...")
        new_df_shopping = df_shopping.copy(deep=True)
        for element in elements_to_delete:
            new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Elementi eliminati!\nRicarica la pagina per vedere i risultati.")
    
    st.markdown("#### Svuota la lista")
    if st.button("Svuota"):
        progress_message = st.text("Svuotamento lista...")
        new_df_shopping = df_shopping.copy(deep=True)
        for element in shopping_list:
            new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Lista svuotata!\nRicarica la pagina per vedere i risultati.")
        

# 3. Debiti
if selected == 'Debiti':
    fighters = ['Andrea', 'Marco', 'Martino']
    debts = df_debts['Soldi'].tolist()

    st.markdown("## Aggiornamento")
    credito = st.number_input(label = "Quanto hai pagato?", step = 1.00)
    debitori = st.multiselect(label = "Per chi hai pagato?",
                   options = fighters,
                   default = None)

    if st.button("Aggiorna debiti"):
        progress_message = st.text(f"Aggiornamento dei debiti in corso...")
        debito = -credito / len(debitori)
        new_df_debts = df_debts.copy(deep=True)
        new_df_debts.loc[new_df_debts['Persona'] == fighter, 'Soldi'] += credito
        for debitore in debitori:
            new_df_debts.loc[new_df_debts['Persona'] == debitore, 'Soldi'] += debito
        conn.update(worksheet="Debts", data=new_df_debts)
        progress_message.text("Aggiornamento completato!\nRicarica la pagina per vedere i risultati.")

    for (fighter, debt) in zip(fighters, debts):
        st.metric(label = 'ciao', value=fighter, delta=round(debt,2), label_visibility='collapsed')
