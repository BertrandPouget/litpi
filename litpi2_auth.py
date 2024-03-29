import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import hmac
import warnings
warnings.filterwarnings("ignore")

# Set page configuration
st.set_page_config(page_title="LitPi", page_icon="🏡")
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
df_chores = conn.read(worksheet="Chores", usecols=list(range(0,5)),nrows=14, ttl=1)
df_shopping = conn.read(worksheet="Shopping", usecols=list(range(0,1)), ttl=1)
df_debts = conn.read(worksheet="Debts", usecols=list(range(0,2)), nrows=3, ttl=1)

#0. Authentication
fighters = ['Andrea', 'Marco', 'Martino']

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.title("Accedi a LitPi🏡")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            st.session_state["fighter"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_password():
    st.stop()

st.title(f"Benvenuto {st.session_state['fighter']}!")

selected = option_menu(
    menu_title = None,
    options = ["Pulizie", "Spesa", 'Debiti'], 
    icons = ['droplet', "list-task", 'piggy-bank'], 
    menu_icon = "cast",
    default_index=0,
    orientation="horizontal")

fighter = st.session_state['fighter']

# 1. Chores
if selected == 'Pulizie':
    st.markdown("### Classifica")
    points = df_chores.copy()
    points[fighters] = points[fighters].multiply(df_chores['Valore'], axis=0)
    rank = points[fighters].sum().sort_values(ascending=False)

    for i, (person, score) in enumerate(rank.items(), 1):
        medal = ":first_place_medal:" if i == 1 else ":second_place_medal:" if i == 2 else ":third_place_medal:" if i == 3 else ""
        st.markdown(f"{medal} **{person}** - *{score} punti*")

    st.markdown("### Aggiornamento")
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

    st.markdown("### Tabella Completa")
    def light_blue_columns(x):
        color = '#f3fafe'
        return f'background-color: {color}'
    
    df_chores = df_chores.style.applymap(lambda x: 'background-color: #f3fafe', subset=df_chores.columns[0:2])
    st.dataframe(df_chores)

# 2. Shopping List
if selected == 'Spesa':

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
    
    if st.button("Svuota"):
        progress_message = st.text("Svuotamento lista...")
        new_df_shopping = df_shopping.copy(deep=True)
        for element in shopping_list:
            new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
        conn.update(worksheet="Shopping", data=new_df_shopping)
        progress_message.text("Lista svuotata!\nRicarica la pagina per vedere i risultati.")
        

# 3. Debts and Credits
if selected == 'Debiti':
    debts = df_debts['Soldi'].tolist()
    st.markdown("### Saldi")
    for (fighter, debt) in zip(fighters, debts):
        st.metric(label = 'ciao', value=fighter, delta=round(debt,2), label_visibility='collapsed')

    st.markdown("### Aggiornamento")
    credit = st.number_input(label = "Quanto hai pagato?", step = 1.00)
    debtors = st.multiselect(label = "Per chi hai pagato?",
                   options = fighters,
                   default = None)

    if st.button("Aggiorna debiti"):
        progress_message = st.text(f"Aggiornamento dei debiti in corso...")
        debito = -credit / len(debtors)
        new_df_debts = df_debts.copy(deep=True)
        new_df_debts.loc[new_df_debts['Persona'] == fighter, 'Soldi'] += credit
        for debtor in debtors:
            new_df_debts.loc[new_df_debts['Persona'] == debtor, 'Soldi'] += debito
        conn.update(worksheet="Debts", data=new_df_debts)
        progress_message.text("Aggiornamento completato!\nRicarica la pagina per vedere i risultati.")
