import streamlit as st
from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Finance & Comm Job Tracker", layout="wide")

st.title("💼 Dashboard de Recherche d'Emploi Spécialisé")
st.markdown("Recherche ciblée pour profils Finance & Communication.")

# --- BARRE LATÉRALE : Paramètres ---
st.sidebar.header("Paramètres de Recherche")

# Liste des postes spécifiques demandés
JOB_ROLES = {
    "Analyste LCB-FT": "Analyste LCB-FT OR KYC OR AML",
    "Analyste ESG": "Analyste ESG OR ISR OR Finance Durable",
    "Chargé de communication": "Chargé de communication OR Communication Officer",
    "Gestion de portefeuille": "Gestion de portefeuille OR Portfolio Manager",
    "Analyste crédit": "Analyste crédit OR Credit Analyst",
    "Analyste financier": "Analyste financier OR Financial Analyst",
    "Correspondance bancaire": "Correspondance bancaire OR Banking Correspondent",
    "Analyste AML-FT": "Analyste AML-FT OR LCB-FT",
    "Chargé de conformité": "Chargé de conformité OR Compliance Officer"
}

selected_role = st.sidebar.selectbox("Poste recherché", list(JOB_ROLES.keys()))
location = st.sidebar.text_input("Localisation", "Paris, France")
distance = st.sidebar.slider("Rayon (km)", 0, 100, 20)
days_old = st.sidebar.slider("Posté depuis (jours)", 1, 30, 2)

# --- LOGIQUE DE RECHERCHE ---
def search_jobs(query, location, days_old):
    try:
        hours = days_old * 24
        with st.spinner(f"Recherche de postes : {query} ({location}, {days_old} jours)..."):
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor"],
                search_term=query,
                location=location,
                distance=distance,
                results_wanted=20,  # Augmenté pour avoir du choix
                hours_old=hours,
                country_indeed='france',
            )
        return jobs
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return pd.DataFrame()

# --- INTERFACE PRINCIPALE ---
st.subheader(f"Résultats pour : {selected_role}")

if st.button("🔍 Lancer la recherche", type="primary"):
    search_query = JOB_ROLES[selected_role]
    # Ajout de guillemets pour forcer l'exactitude si besoin, ou refine query
    # Pour jobspy, une query précise sans opérateurs booléens complexes marche souvent mieux sur tous les sites,
    # mais essayons d'être précis.
    
    results = search_jobs(search_query, location, days_old)
    
    if not results.empty:
        st.success(f"{len(results)} offres trouvées.")
        
        # Nettoyage et affichage
        display_cols = ['title', 'company', 'location', 'date_posted', 'job_url']
        # On filtre les colonnes qui existent vraiment
        cols_to_show = [c for c in display_cols if c in results.columns]
        
        # Formatage des liens pour être cliquables
        st.data_editor(
            results[cols_to_show],
            column_config={
                "job_url": st.column_config.LinkColumn("Lien de l'offre"),
                "date_posted": st.column_config.DateColumn("Date de publication")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.divider()
        st.subheader("Détails des offres")
        for index, row in results.iterrows():
            with st.expander(f"{row['title']} chez {row['company']}"):
                st.write(f"**Lieu:** {row.get('location', 'N/A')}")
                st.write(f"**Date:** {row.get('date_posted', 'N/A')}")
                st.write(f"**Description:**")
                st.write(row.get('description', 'Pas de description disponible.'))
                st.link_button("Postuler", row['job_url'])
                
    else:
        st.warning("Aucune offre trouvée correspondant exactement à ces critères. Essayez d'élargir le rayon ou le nombre de jours.")

st.sidebar.divider()
st.sidebar.info("Astuce : Si vous avez trop peu de résultats, augmentez la durée de recherche (jours).")
