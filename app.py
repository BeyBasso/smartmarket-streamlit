import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os

st.set_page_config(page_title="SmartMarket - Marketing Analytics", page_icon="🛒", layout="wide")

DATA_DIR = "data"
LEADS_PATH = os.path.join(DATA_DIR, "leads_smartmarket.csv")
CAMP_PATH = os.path.join(DATA_DIR, "campaign_smartmarket.json")
CRM_PATH = os.path.join(DATA_DIR, "crm_smartmarket.xlsx")

PERIMETER_START = pd.Timestamp("2025-09-01")
PERIMETER_END = pd.Timestamp("2025-09-30")

STATUS_ORDER = ["MQL", "SQL", "Client"]


def stop_if_missing_files():
    missing = [p for p in [LEADS_PATH, CAMP_PATH, CRM_PATH] if not os.path.exists(p)]
    if missing:
        st.error("Fichiers manquants :\n- " + "\n- ".join(missing))
        st.stop()


@st.cache_data
def load_data():
    stop_if_missing_files()

    leads = pd.read_csv(LEADS_PATH)
    leads["date"] = pd.to_datetime(leads["date"], errors="coerce")

    with open(CAMP_PATH, "r", encoding="utf-8") as f:
        campaigns = pd.DataFrame(json.load(f))

    crm = pd.read_excel(CRM_PATH)

    for df in [leads, campaigns, crm]:
        for c in df.select_dtypes(include="object").columns:
            df[c] = df[c].astype(str).str.strip()

    leads["lead_id"] = leads["lead_id"].astype(str)
    crm["lead_id"] = crm["lead_id"].astype(str)

    return leads, campaigns, crm


def filter_perimeter(leads):
    return leads[(leads["date"] >= PERIMETER_START) & (leads["date"] <= PERIMETER_END)].copy()


def build_mart(leads, campaigns, crm):
    df = leads.merge(crm, on="lead_id", how="left", validate="one_to_one")
    camp = campaigns.groupby("channel", as_index=False).agg(
        cost=("cost", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
    )
    df = df.merge(camp, on="channel", how="left")
    df["is_client"] = (df["status"] == "Client").astype(int)
    return df


def safe_rate(num, den):
    return num / den if den else np.nan


def fmt_int(x):
    return f"{int(x):,}".replace(",", " ")


def fmt_eur(x):
    return f"{x:,.0f} €".replace(",", " ")


def fmt_eur_2(x):
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def fmt_pct(x):
    return f"{x:.2%}".replace(".", ",")


def fmt_pct_1(x):
    return f"{x:.1%}".replace(".", ",")


leads_raw, campaigns_raw, crm_raw = load_data()
leads = filter_perimeter(leads_raw).drop_duplicates("lead_id")
mart = build_mart(leads, campaigns_raw, crm_raw)

ALL_CHANNELS = sorted(mart["channel"].dropna().unique())
ALL_REGIONS = sorted(mart["region"].dropna().unique())

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Aller à :",
    [
        "🏠 Accueil",
        "✅ Sélection des données",
        "📈 Analyse",
        "📊 Visualisations",
        "📌 Dashboard",
        "📝 Note d’analyse métier",
        "🛠️ Carnet technique",
    ],
)

if page not in ["🏠 Accueil", "📝 Note d’analyse métier", "🛠️ Carnet technique"]:
    st.subheader("Filtres")
    c1, c2, c3 = st.columns([3, 3, 1])

    with c1:
        selected_channels = st.multiselect("Canaux", options=ALL_CHANNELS)
    with c2:
        selected_regions = st.multiselect("Régions", options=ALL_REGIONS)
    with c3:
        st.write("")
        st.write("")
        reset = st.button("Réinitialiser")

    if reset:
        selected_channels = []
        selected_regions = []

    channels_to_use = selected_channels if selected_channels else ALL_CHANNELS
    regions_to_use = selected_regions if selected_regions else ALL_REGIONS

    mart_f = mart[(mart["channel"].isin(channels_to_use)) & (mart["region"].isin(regions_to_use))].copy()

    st.caption(
        "CTR = clics / impressions · CVR = conversions / clics · CPL = coût / leads · "
        "Taux client = clients CRM / leads"
    )
    st.divider()
else:
    channels_to_use = ALL_CHANNELS
    regions_to_use = ALL_REGIONS
    mart_f = mart.copy()


if page == "🏠 Accueil":
    st.title("🛒 SmartMarket — Analyse Marketing Multi-Canaux")

    st.markdown(
        """
SmartMarket analyse la performance de ses campagnes marketing sur **septembre 2025** afin d’aider la direction à **prioriser les canaux** et **optimiser le budget**.

Cette application propose :
- une **sélection des données** (périmètre + variables retenues),
- une **analyse univariée et bivariée**,
- des **visualisations métier**,
- un **dashboard** synthétique (KPI),
- une **note d’analyse métier** et un **carnet technique**.
        """
    )

    st.divider()

    st.subheader("Objectifs métier")
    st.markdown(
        """
- Mesurer la performance marketing (**CTR**, **CVR**, **CPL**).
- Mesurer la performance business via le CRM (**MQL → SQL → Client**).
- Identifier les segments les plus rentables (**région**, **secteur**, **taille d’entreprise**).
- Proposer des recommandations opérationnelles d’optimisation.
        """
    )

    st.divider()

    st.subheader("Périmètre & sources de données")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
**Périmètre**
- Période analysée : **01/09/2025 → 30/09/2025**
- Unités analysées : **leads** (CRM) + **campagnes** (media)
            """
        )

    with c2:
        st.markdown(
            """
**Sources**
- `leads_smartmarket.csv` : date, canal, device  
- `campaign_smartmarket.json` : coût, impressions, clics, conversions  
- `crm_smartmarket.xlsx` : secteur, région, taille, statut (MQL/SQL/Client)
            """
        )

    st.divider()

    st.subheader("Définitions des KPI")
    st.markdown(
        """
- **CTR** = clics / impressions → efficacité publicitaire (capacité à générer du trafic).  
- **CVR** = conversions / clics → efficacité post-clic (capacité à convertir).  
- **CPL** = coût / leads → coût d’acquisition d’un lead.  
- **Taux client (CRM)** = clients / leads → qualité business finale.

⚠️ Les **conversions campagnes** ne sont pas forcément des **clients CRM** : l’application affiche ces indicateurs séparément.
        """
    )

    st.divider()

    st.subheader("📊 Aperçu rapide des données (périmètre)")
    leads_period = filter_perimeter(leads_raw)
    mart_period = build_mart(leads_period.drop_duplicates("lead_id"), campaigns_raw, crm_raw)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Leads (sept. 2025)", fmt_int(len(leads_period)))
    k2.metric("Canaux", fmt_int(mart_period["channel"].nunique()))
    k3.metric("Régions", fmt_int(mart_period["region"].nunique()))
    k4.metric("Secteurs", fmt_int(mart_period["sector"].nunique()))

    st.divider()

    st.subheader("Comment utiliser l’application")
    st.markdown(
        """
1. Va dans **Sélection des données** pour vérifier le périmètre et les variables retenues.  
2. Consulte **Analyse** pour les tableaux uni/bivariés et leurs interprétations.  
3. Consulte **Visualisations** pour répondre aux questions métier clés.  
4. Utilise **Dashboard** pour une lecture rapide (KPI + graphs) et exporter les résultats si nécessaire.  
        """
    )

    st.info(
        "Les filtres (Canaux / Régions) s’appliquent sur les pages Analyse, Visualisations, Dashboard. "
        "Ils ne s’appliquent pas à l’Accueil, la Note métier, ni au Carnet technique."
    )

    

elif page == "✅ Sélection des données":
    st.title("✅ Sélection des données")

    leads_period = filter_perimeter(leads_raw)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads bruts", fmt_int(len(leads_raw)))
    c2.metric("Leads périmètre", fmt_int(len(leads_period)))
    c3.metric("Leads analysés", fmt_int(len(mart_f)))
    c4.metric("Doublons supprimés", fmt_int(len(leads_period) - len(leads)))

    st.markdown(
        """
Variables conservées :
- Leads : `lead_id`, `date`, `channel`, `device`
- Campagnes : `cost`, `impressions`, `clicks`, `conversions`
- CRM : `company_size`, `sector`, `region`, `status`

Justification :
- `date` applique le périmètre (septembre 2025).
- `channel` permet de comparer la performance par canal.
- `region/sector/company_size` permettent la segmentation.
- `status` mesure la qualité business (MQL/SQL/Client).
- Toute donnée identifiante est exclue.
        """
    )

    with st.expander("Aperçu des données filtrées"):
        st.dataframe(mart_f.head(50), use_container_width=True)

    st.download_button(
        "📥 Exporter les données filtrées (CSV)",
        mart_f.to_csv(index=False).encode("utf-8"),
        "smartmarket_donnees_filtrees.csv",
        "text/csv",
    )

elif page == "📈 Analyse":
    st.title("📈 Analyse univariée & bivariée")

    st.subheader("Univariée (qualitative)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Leads par canal**")
        st.dataframe(mart_f["channel"].value_counts().to_frame("nb_leads"), use_container_width=True)

        st.markdown("**Statut CRM**")
        st.dataframe(
            mart_f["status"].value_counts().reindex(STATUS_ORDER).dropna().to_frame("nb_leads"),
            use_container_width=True,
        )

    with col2:
        st.markdown("**Leads par région**")
        st.dataframe(mart_f["region"].value_counts().to_frame("nb_leads"), use_container_width=True)

        st.markdown("**Leads par secteur**")
        st.dataframe(mart_f["sector"].value_counts().to_frame("nb_leads"), use_container_width=True)

    st.divider()
    st.subheader("Univariée (quantitative) – campagnes")
    stats = campaigns_raw[["cost", "impressions", "clicks", "conversions"]].describe().T
    stats = stats[["mean", "50%", "min", "max"]].rename(columns={"50%": "median"})
    st.dataframe(stats.round(2), use_container_width=True)

    st.divider()
    st.subheader("Bivariée (relations métier)")

    st.markdown("**Canal × Statut CRM (en % par canal)**")
    pivot = pd.crosstab(mart_f["channel"], mart_f["status"], normalize="index") * 100
    st.dataframe(pivot.round(1), use_container_width=True)

    st.markdown("**Taux client par région**")
    reg = mart_f.groupby("region", as_index=False)["is_client"].mean()
    reg["taux_client_%"] = reg["is_client"] * 100
    st.dataframe(reg.sort_values("taux_client_%", ascending=False)[["region", "taux_client_%"]].round(1))

    st.markdown("**Taux client par secteur**")
    sec = mart_f.groupby("sector", as_index=False)["is_client"].mean()
    sec["taux_client_%"] = sec["is_client"] * 100
    st.dataframe(sec.sort_values("taux_client_%", ascending=False)[["sector", "taux_client_%"]].round(1))

    st.info(
        """
**Interprétation métier**
- Le croisement Canal × Statut distingue les canaux orientés volume (MQL) des canaux orientés qualité (SQL/Client).
- Les segments (région, secteur) avec un taux client supérieur à la moyenne sont prioritaires pour le ciblage.
- Les statistiques de campagnes aident à détecter des extrêmes de coûts ou de performance.
        """
    )

elif page == "📊 Visualisations":
    st.title("📊 Visualisations")

    vc = mart_f["channel"].value_counts().reset_index()
    vc.columns = ["channel", "nb_leads"]
    st.plotly_chart(px.bar(vc, x="channel", y="nb_leads", title="Volume de leads par canal"), use_container_width=True)

    grp = mart_f.groupby(["channel", "status"], as_index=False).size()
    st.plotly_chart(
        px.bar(grp, x="channel", y="size", color="status", barmode="group", title="Qualité des leads : statut CRM par canal"),
        use_container_width=True,
    )

    reg = mart_f.groupby("region", as_index=False)["is_client"].mean()
    reg["taux_client_%"] = reg["is_client"] * 100
    st.plotly_chart(
        px.bar(reg.sort_values("taux_client_%", ascending=False), x="region", y="taux_client_%", title="Taux de clients par région"),
        use_container_width=True,
    )

    camp_ch = campaigns_raw.groupby("channel", as_index=False).agg(
        cost=("cost", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
    )
    camp_ch["CTR"] = np.where(camp_ch["impressions"] > 0, camp_ch["clicks"] / camp_ch["impressions"], np.nan)
    camp_ch["CVR"] = np.where(camp_ch["clicks"] > 0, camp_ch["conversions"] / camp_ch["clicks"], np.nan)
    melt = camp_ch.melt(id_vars="channel", value_vars=["CTR", "CVR"], var_name="metric", value_name="value")

    st.plotly_chart(
        px.line(melt, x="channel", y="value", color="metric", markers=True, title="CTR et conversion (clic→conversion) par canal"),
        use_container_width=True,
    )

    leads_by_channel = mart_f.groupby("channel", as_index=False).agg(nb_leads=("lead_id", "count"))
    cpl = leads_by_channel.merge(camp_ch[["channel", "cost"]], on="channel", how="left")
    cpl["CPL"] = np.where(cpl["nb_leads"] > 0, cpl["cost"] / cpl["nb_leads"], np.nan)

    st.plotly_chart(
        px.bar(cpl.sort_values("CPL", ascending=False), x="channel", y="CPL", title="Coût par lead (CPL) estimé par canal"),
        use_container_width=True,
    )

    st.info(
        """
**Interprétation**
- CTR élevé sans conversion : améliorer le ciblage, le message ou la landing.
- CPL élevé peut être acceptable si la qualité CRM (taux client) est élevée.
- L’analyse régionale aide à concentrer le budget sur les zones les plus rentables.
        """
    )

elif page == "📌 Dashboard":
    st.title("📌 Dashboard")

    total_leads = len(mart_f)

    camp_filtered = campaigns_raw[campaigns_raw["channel"].isin(channels_to_use)].copy()
    total_cost = camp_filtered["cost"].sum()
    total_impr = camp_filtered["impressions"].sum()
    total_clicks = camp_filtered["clicks"].sum()
    total_conv = camp_filtered["conversions"].sum()

    ctr = safe_rate(total_clicks, total_impr)
    cvr = safe_rate(total_conv, total_clicks)
    cpl = safe_rate(total_cost, total_leads)
    client_rate = mart_f["is_client"].mean() if total_leads > 0 else np.nan

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Leads", fmt_int(total_leads))
    k2.metric("Coût total", fmt_eur(total_cost))
    k3.metric("CTR", fmt_pct(ctr) if pd.notna(ctr) else "—")
    k4.metric("CVR", fmt_pct(cvr) if pd.notna(cvr) else "—")
    k5.metric("CPL", fmt_eur_2(cpl) if pd.notna(cpl) else "—")
    k6.metric("Taux client", fmt_pct_1(client_rate) if pd.notna(client_rate) else "—")

    st.caption("CTR = clics / impressions · CVR = conversions / clics · CPL = coût / leads · Taux client = clients CRM / leads")
    st.divider()

    left, right = st.columns(2)

    rate_ch = mart_f.groupby("channel", as_index=False)["is_client"].mean()
    rate_ch["taux_client_%"] = rate_ch["is_client"] * 100
    left.plotly_chart(
        px.bar(rate_ch.sort_values("taux_client_%", ascending=False), x="channel", y="taux_client_%", title="Taux client par canal"),
        use_container_width=True,
    )

    camp_cost = campaigns_raw.groupby("channel", as_index=False).agg(cost=("cost", "sum"))
    leads_ch = mart_f.groupby("channel", as_index=False).agg(nb_leads=("lead_id", "count"))
    cpl_ch = leads_ch.merge(camp_cost, on="channel", how="left")
    cpl_ch["CPL"] = np.where(cpl_ch["nb_leads"] > 0, cpl_ch["cost"] / cpl_ch["nb_leads"], np.nan)

    right.plotly_chart(
        px.bar(cpl_ch.sort_values("CPL", ascending=False), x="channel", y="CPL", title="CPL par canal"),
        use_container_width=True,
    )

    st.info(
        """
**Lecture rapide**
- Prioriser les canaux avec **taux client élevé** et **CPL raisonnable**.
- CTR élevé + CVR faible : travailler la landing, le ciblage ou la proposition de valeur.
- Les segments régionaux/sectoriels performants méritent des campagnes dédiées.
        """
    )

    kpi_export = pd.DataFrame(
        {
            "kpi": ["leads", "cout_total", "ctr", "cvr", "cpl", "taux_client"],
            "value": [total_leads, total_cost, ctr, cvr, cpl, client_rate],
        }
    )

    st.download_button(
        "📥 Exporter les KPI (CSV)",
        kpi_export.to_csv(index=False).encode("utf-8"),
        "smartmarket_kpi.csv",
        "text/csv",
    )

elif page == "📝 Note d’analyse métier":
    st.title("📝 Note d’analyse métier")

    st.markdown(
        """
### Contexte et objectifs
SmartMarket a déployé plusieurs campagnes marketing au cours de septembre 2025 afin de générer des leads.
L’objectif est de comparer les canaux d’acquisition et d’identifier les segments les plus rentables pour optimiser le budget.

### Données et périmètre
Trois sources ont été exploitées : leads, campagnes et CRM.
Le périmètre est limité à septembre 2025. Les doublons sur lead_id sont supprimés pour éviter de fausser les indicateurs.

### Résultats clés
Les canaux présentent des profils de performance différents : certains génèrent surtout du volume, d’autres moins de leads mais une meilleure conversion finale en clients.
Les KPI marketing (CTR, CVR) mesurent l’efficacité média, mais la performance business se mesure via le CRM (taux de clients).

La segmentation (région, secteur, taille) met en évidence des zones où la conversion en clients est supérieure à la moyenne, ce qui indique des opportunités de ciblage.

### Interprétation métier
Un canal doit être évalué selon le couple coût/qualité :
- CPL faible est intéressant si la qualité CRM suit,
- un canal plus coûteux peut être rentable s’il génère proportionnellement plus de clients.

CTR élevé sans conversion suggère un défaut d’alignement entre la promesse publicitaire et le parcours (landing, offre, ciblage).

### Recommandations
1. Réallouer le budget vers les canaux au meilleur équilibre CPL / taux client.
2. Optimiser les canaux à CTR correct mais CVR faible (tests A/B landing, message, ciblage).
3. Renforcer les campagnes sur les segments (régions/secteurs) les plus convertisseurs.
4. Aligner marketing et ventes : distinguer conversions marketing et clients CRM, suivre MQL → SQL → Client.
        """
    )

elif page == "🛠️ Carnet technique":
    st.title("🛠️ Carnet technique")

    st.markdown(
        """
**1) Streamlit non installé / mauvais interpréteur**
- Problème : ModuleNotFoundError car l’environnement Python utilisé n’était pas celui où Streamlit était installé.
- Solution : création d’un venv, installation des packages, sélection de l’interpréteur `.venv`.
- Justification : reproductibilité et isolation des dépendances.

**2) Fichiers introuvables**
- Problème : l’application échoue si les fichiers ne sont pas dans `data/`.
- Solution : contrôle au démarrage et arrêt propre avec message clair.
- Justification : diagnostic rapide et fiable.

**3) Nettoyage des colonnes texte**
- Problème : espaces et libellés incohérents faussent les groupby.
- Solution : `str.strip()` sur toutes les colonnes texte.
- Justification : fiabilité des KPI.

**4) Doublons lead_id**
- Problème : les doublons gonflent artificiellement les volumes.
- Solution : suppression via `drop_duplicates("lead_id")`.
- Justification : cohérence des indicateurs.

**5) Divisions par zéro**
- Problème : CTR/CVR peuvent être infinis si impressions ou clics = 0.
- Solution : fonction safe_rate() et contrôles des dénominateurs.
- Justification : stabilité des calculs et indicateurs interprétables.

**6) Conversion marketing vs client CRM**
- Problème : risque de confondre conversions de campagnes et clients finaux.
- Solution : affichage séparé + note explicative dans le dashboard.
- Justification : éviter une décision budgétaire erronée.
        """
    )


st.markdown("---")
st.caption("Projet SmartMarket – Analyse marketing – Périmètre : Septembre 2025")
