import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import warnings
warnings.filterwarnings("ignore")

st.title("LitPi\n Streamlit per Casa Lippi")

conn = st.connection("gsheets", type=GSheetsConnection)
df_chores = conn.read(worksheet="Chores", usecols=list(range(0,5)),
                       nrows=14, ttl=5)

st.markdown("## Classifica")
points = df_chores.copy()
points[['Andrea', 'Martino', 'Marco']] = points[['Andrea', 'Martino', 'Marco']].multiply(df_chores['Valore'], axis=0)
rank = points[['Andrea', 'Martino', 'Marco']].sum().sort_values(ascending=False)
for i, (name, score) in enumerate(rank.items(), 1):
    medal = ":first_place_medal:" if i == 1 else ":second_place_medal:" if i == 2 else ":third_place_medal:" if i == 3 else ""
    st.markdown(f"{medal} **{name}** - *{score} punti*")

st.markdown("## Tabella Completa")
st.dataframe(df_chores)

st.markdown("## Aggiornamento")

fighter = st.radio(label = "Chi sei?",
                   options = ("Andrea", "Marco", "Martino"),
                   index = None)


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



