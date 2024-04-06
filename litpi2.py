import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from streamlit_image_select import image_select
from datetime import date
import warnings
warnings.filterwarnings("ignore")

# Set page configuration
st.set_page_config(page_title="Litpi", page_icon="🏡")
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

#0. Authentication
st.title("Benvenuto su Litpi:house:")
fighters = ['Andrea', 'Marco', 'Martino']

fighter_img = image_select(
    label="Seleziona il tuo personaggio",
    images=[
        "images/andrea.jpg",
        "images/marco.jpg",
        "images/martino.jpg",
    ],
    captions=["Andrea", "Marco", "Martino"],
    use_container_width=False
)

if fighter_img == "images/andrea.jpg":
    fighter = "Andrea"
if fighter_img == "images/marco.jpg":
    fighter = "Marco"
if fighter_img == "images/martino.jpg":
    fighter = "Martino"

selected = option_menu(
    menu_title = None,
    options = ["Pulizie", "Spesa", 'Debiti'], 
    icons = ['droplet', "list-task", 'piggy-bank'], 
    menu_icon = "cast",
    default_index=0,
    orientation="horizontal")


# 1. Chores
if selected == 'Pulizie':
    df_chores_all = conn.read(worksheet="Chores", ttl=1)
    df_chores = df_chores_all.iloc[0:14, 0:5]
    df_chores_history = df_chores_all.iloc[:, 6:9]

    hist_rows = 10
    df_chores_history.dropna(axis=0, inplace=True)

    st.markdown("### Classifica")
    points = df_chores.copy()
    points[fighters] = points[fighters].multiply(df_chores['Valore'], axis=0)
    rank = points[fighters].sum().sort_values(ascending=False)

    for i, (person, score) in enumerate(rank.items(), 1):
        medal = ":first_place_medal:" if i == 1 else ":second_place_medal:" if i == 2 else ":third_place_medal:" if i == 3 else ""
        st.markdown(f"{medal} **{person}** - *{score:.0f} punti*")

    st.markdown("### Aggiornamento")
    chores = st.multiselect(label = "Seleziona i compiti che hai fatto",
                        options = df_chores.loc[:, "Compito"].tolist(),
                        default = None)

    if st.button("Conferma"):
        progress_message = st.text(f"Aggiornamento dei lavori di {fighter} in corso...")
        new_df_chores = df_chores.copy(deep=True)
        for chore in chores:
            new_df_chores.loc[new_df_chores['Compito'] == chore, fighter] += 1

        new_df_chores_history = df_chores_history.copy(deep=True)
        new_df_chores_history = pd.concat([ pd.DataFrame([[fighter, date.today().strftime("%d/%m/%Y"), ', '.join(chores)]], columns=new_df_chores_history.columns), new_df_chores_history], ignore_index=True)

        new_df_chores_all = pd.concat([new_df_chores, pd.DataFrame([[""]], columns=[""]), new_df_chores_history], axis=1)
        conn.update(worksheet="Chores", data=new_df_chores_all)

        progress_message.text("Aggiornamento completato!\nRicarica la pagina per vedere i risultati.")

        st.rerun()


    st.markdown("### Storico")

    people = df_chores_history['Persona'].tolist()
    dates = df_chores_history['Quando'].tolist()
    actions = df_chores_history['Cosa'].tolist()
    
    for (i, person, date, action) in zip(range(hist_rows), people, dates, actions):
        st.markdown(f""" - {date}  
        **{person}** si è segnato **{action}** """)


    st.markdown("### Tabella Completa")
    
    df_chores_style = df_chores.style \
        .applymap(lambda x: 'background-color: #fdf1d6', subset=df_chores.columns[0:2]) \
        .format(precision=0, thousands="'", decimal=".")
    st.dataframe(df_chores_style)


    



# 2. Shopping List
if selected == 'Spesa':
    df_shopping = conn.read(worksheet="Shopping", usecols=list(range(0,1)), ttl=1)

    shopping_list = df_shopping['Spesa'].dropna().tolist()
    st.markdown("### Lista")
    if shopping_list == []:
        st.markdown("La lista della spesa è vuota")
    else:
        for i, item in enumerate(shopping_list):
            st.markdown(f"{i+1}. {item}")

    st.markdown("### Aggiornamento")
    user_input = st.text_input("Aggiungi un elemento alla lista:")
    if st.button("Aggiungi"):
        progress_message = st.text("Aggiunta elemento...")
        new_df_shopping = df_shopping.copy(deep=True)
        new_df_shopping = pd.concat([pd.DataFrame({'Spesa': [user_input]}), df_shopping], ignore_index=True)
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Elemento aggiunto!\nRicarica la pagina per vedere i risultati.")

        st.rerun()

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

        st.rerun()
    
    if st.button("Svuota"):
        progress_message = st.text("Svuotamento lista...")
        new_df_shopping = df_shopping.copy(deep=True)
        for element in shopping_list:
            new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Lista svuotata!\nRicarica la pagina per vedere i risultati.")

        st.rerun()


# 3. Debts and Credits
if selected == 'Debiti':
    df_debts_all = conn.read(worksheet="Debts", ttl=1)
    df_debts = df_debts_all.iloc[0:3, 0:2]
    df_debts_history = df_debts_all.iloc[:, 3:8]

    hist_rows = 10
    df_debts_history.dropna(axis=0, subset=["Creditore"], inplace=True)

    debts = df_debts['Bilancio'].tolist()

    st.markdown("### Saldi")
    for (person, debt) in zip(fighters, debts):
        st.metric(label = 'ciao', value=person, delta=str(round(debt,2))+'€', label_visibility='collapsed')

    st.markdown("### Aggiornamento")
    credit = st.number_input(label = "Quanto hai pagato?", step = 1.00)
    debtors = st.multiselect(label = "Per chi hai pagato?",
                   options = fighters,
                   default = None)
    reason = st.text_input(label = "Causale?", placeholder="Causale")

    if st.button("Aggiorna debiti"):
        progress_message = st.text(f"Aggiornamento dei crediti di {fighter} in corso...")
        debit = -credit / len(debtors)
        new_df_debts = df_debts.copy(deep=True)
        new_df_debts.loc[new_df_debts['Persona'] == fighter, 'Bilancio'] += credit
        for debtor in debtors:
            new_df_debts.loc[new_df_debts['Persona'] == debtor, 'Bilancio'] += debit

        new_df_debts_history = df_debts_history.copy(deep=True)
        new_df_debts_history = pd.concat([ pd.DataFrame([[fighter, credit, ', '.join(debtors), date.today().strftime("%d/%m/%Y"), reason]], columns=new_df_debts_history.columns), new_df_debts_history], ignore_index=True)
        
        new_df_debts_all = pd.concat([new_df_debts, pd.DataFrame([[""]], columns=[""]), new_df_debts_history], axis=1)
        conn.update(worksheet="Debts", data=new_df_debts_all)

        progress_message.text("Aggiornamento completato!\nRicarica la pagina per vedere i risultati.")

        st.rerun()


    st.markdown("### Storico")

    creditors = df_debts_history['Creditore'].tolist()
    transactions = df_debts_history['Soldi'].tolist()
    debtors = df_debts_history['Debitori'].tolist()
    dates = df_debts_history['Data'].tolist()
    reasons = df_debts_history['Causale'].tolist()
    
    for (i, creditor, transaction, debtor, date, reason) in zip(range(hist_rows), creditors, transactions, debtors, dates, reasons):
        # st.markdown(f" - {date}: {creditor} ha pagato {transaction:.2f}€ per {debtor}. Causale: {reason}")

        if debtor.find("Andrea") != -1 and debtor.find("Marco") != -1 and debtor.find("Martino") != -1: 
            debtor = "Tutti"
        st.markdown(f""" - {date}: **{transaction:.2f}€** per *{reason}*  
        Pagato da <span style="color:green">**{creditor}**</span> per <span style="color:red">**{debtor}**</span>""", unsafe_allow_html=True)
