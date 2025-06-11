import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from streamlit_image_select import image_select
import warnings

from modules import chores, shopping, debts

warnings.filterwarnings("ignore")

# --- CONFIGURAZIONE PAGINA ---
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

# --- COSTANTI GLOBALI ---
FIGHTERS = ['Andrea', 'Marco', 'Martino']
FIGHTER_IMAGES = [
    "images/andrea.jpg",
    "images/marco.jpg",
    "images/martino.jpg",
]

def main():
    """Funzione principale che esegue l'applicazione Streamlit."""
    
    st.title("Litpi:house:")

    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- SELEZIONE UTENTE ---
    fighter = None
    fighter_img = image_select(
        label="Seleziona il tuo personaggio",
        images=FIGHTER_IMAGES,
        captions=FIGHTERS,
        use_container_width=False
    )

    if fighter_img == "images/andrea.jpg":
        fighter = "Andrea"
    if fighter_img == "images/marco.jpg":
        fighter = "Marco"
    if fighter_img == "images/martino.jpg":
        fighter = "Martino"

    # --- MENU DI NAVIGAZIONE ---
    selected_page = option_menu(
        menu_title=None,
        options=["Pulizie", "Spesa", 'Debiti'],
        icons=['droplet', "list-task", 'piggy-bank'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )

    # --- ROUTER DI PAGINA ---
    if selected_page == 'Pulizie':
        chores.render(conn, fighter, FIGHTERS)
    
    elif selected_page == 'Spesa':
        shopping.render(conn)
    
    elif selected_page == 'Debiti':
        debts.render(conn, fighter, FIGHTERS)

if __name__ == "__main__":
    main()