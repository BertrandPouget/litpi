import streamlit as st
import pandas as pd

WORKSHEET_NAME = "Shopping"

def render(conn):
    """Funzione principale per renderizzare la pagina della lista della spesa."""
    # 1. LETTURA DATI
    df_shopping = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(0, 1)), ttl=1)
    shopping_list = df_shopping['Spesa'].dropna().tolist()

    # 2. VISUALIZZAZIONE LISTA
    st.markdown("### Lista")
    if not shopping_list:
        st.markdown("La lista della spesa è vuota")
    else:
        for i, item in enumerate(shopping_list, 1):
            st.markdown(f"{i}. {item}")

    # 3. AGGIORNAMENTO (logica originale)
    st.markdown("### Aggiornamento")
    user_input = st.text_input("Aggiungi un elemento alla lista:")
    if st.button("Aggiungi"):
        if user_input:
            progress_message = st.text("Aggiunta elemento...")
            new_df_shopping = pd.DataFrame({'Spesa': [user_input]})
            updated_df = pd.concat([new_df_shopping, df_shopping], ignore_index=True)
            conn.update(worksheet=WORKSHEET_NAME, data=updated_df)
            st.rerun()

    elements_to_delete = st.multiselect(
        label="Seleziona gli elementi da eliminare",
        options=shopping_list,
        default=None
    )
    if st.button("Elimina"):
        if elements_to_delete:
            progress_message = st.text("Eliminazione elementi...")
            new_df_shopping = df_shopping.copy()
            for element in elements_to_delete:
                new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
            conn.update(worksheet=WORKSHEET_NAME, data=new_df_shopping)
            st.rerun()
    
    if st.button("Svuota"):
        progress_message = st.text("Svuotamento lista...")
        new_df_shopping = df_shopping.copy()
        for element in shopping_list:
            new_df_shopping.loc[new_df_shopping['Spesa'] == element, 'Spesa'] = None
        conn.update(worksheet=WORKSHEET_NAME, data=new_df_shopping)
        st.rerun()