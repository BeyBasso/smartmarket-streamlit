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
    f1, f2 = st.columns(2)
    with f1:
        selected_channels = st.multiselect("Canaux", options=ALL_CHANNELS)
    with f2:
        selected_regions = st.multiselect("Régions", options=ALL_REGIONS)

    channels_to_use = selected_channels if selected_channels else ALL_CHANNELS
    regions_to_use = selected_regions if selected_regions else ALL_REGIONS

    mart_f = mart[(mart["channel"].isin(channels_to_use)) & (mart["region"].isin(regions_to_use))].copy()
    st.divider()
else:
    channels_to_use = ALL_CHANNELS
    regions_to_use = ALL_REGIONS
    mart_f = mart.copy()


if page == "🏠 Accueil":
    st.title("🛒 SmartMarket — Analyse Marketing Multi-Canaux")
    st.markdown(
        """
SmartMarket analyse la performance de ses campagnes sur **septembre 2025**.

Objectifs :
- mesurer la performance marketing (CTR, conversions),
- mesurer la performance business via le CRM (MQL → SQL → Client),
- identifier les segments (région, secteur, taille) les plus rentables,
- recommander des actions d’optimisation.
        """
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
- `channel` permet de comparer la performance par canal.
- `region/sector/company_size` permettent la segmentation.
- `status` permet de mesurer la qualité business du lead.
- Toute donnée identifiante est exclue.
        """
    )

    with st.expander("Aperçu des données filtrées"):
        st.dataframe(mart_f.head(50), use_container_width=True)

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

    st.divider()
    st.subheader("Interprétation")
    st.markdown(
        """
- Le croisement **Canal × Statut** sépare les canaux orientés volume (MQL) des canaux orientés qualité (SQL/Client).
- Les taux client par **région** et **secteur** identifient les segments où la conversion finale est plus élevée.
- Les statistiques descriptives des campagnes permettent de comparer les niveaux de coûts et d’identifier des extrêmes.
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

    st.divider()
    st.subheader("Interprétation")
    st.markdown(
        """
- Un canal peut être performant en CTR mais faible en conversion : cela indique souvent une optimisation à faire sur le ciblage ou la landing.
- Le CPL doit être analysé avec la qualité CRM : un CPL élevé est acceptable si le taux client est très bon.
- L’analyse régionale permet de cibler des zones géographiques plus rentables.
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

    st.divider()
    st.subheader("Lecture rapide pour décision")
    st.markdown(
        """
- Investir prioritairement sur les canaux avec **taux client élevé** et **CPL raisonnable**.
- Sur un canal à CTR élevé mais CVR faible : améliorer ciblage, message ou landing.
- Concentrer les efforts sur les régions et secteurs dont le taux client est supérieur à la moyenne.
        """
    )

elif page == "📝 Note d’analyse métier":
    st.title("📝 Note d’analyse métier")

    st.markdown(
        """
### Contexte et objectifs
SmartMarket a déployé plusieurs campagnes marketing au cours de septembre 2025 pour générer des leads.
L’objectif est de mesurer la performance des canaux d’acquisition et d’identifier les segments les plus rentables afin d’optimiser le budget.

### Données et périmètre
Trois sources ont été exploitées : leads, campagnes et CRM.
Le périmètre est limité à septembre 2025. Les doublons de lead_id sont supprimés pour éviter de fausser les volumes et KPI.

### Résultats clés
Les canaux ne présentent pas les mêmes profils de performance :
- certains canaux apportent davantage de volume,
- d’autres apportent moins de leads mais une meilleure conversion finale en clients.

Les KPI marketing (CTR et CVR) expliquent l’efficacité média, mais le CRM permet d’évaluer la qualité business avec la part de clients.

L’analyse de segmentation (région, secteur, taille) met en évidence des zones et profils où la conversion en client est supérieure à la moyenne, ce qui constitue des opportunités de ciblage.

### Interprétation métier
Un canal doit être jugé par son équilibre coût / qualité :
- un CPL bas est intéressant uniquement si la qualité suit,
- un canal coûteux peut rester rentable s’il génère proportionnellement plus de clients.

Un CTR élevé sans conversion suggère un défaut d’alignement entre la promesse publicitaire et le parcours de conversion (ciblage, offre, landing page).

### Recommandations
1. Réallouer le budget vers les canaux à taux client élevé et CPL acceptable.
2. Optimiser les canaux à CTR correct mais CVR faible : tests A/B sur landing, ciblage et message.
3. Renforcer les campagnes sur les régions et secteurs les plus convertisseurs.
4. Mieux aligner marketing et ventes : distinguer conversion marketing et client CRM, suivre le funnel MQL → SQL → Client.
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
- Solution : fonction `safe_rate()` et contrôle des dénominateurs.
- Justification : stabilité du calcul et meilleure lisibilité.

**6) Conversion marketing vs client CRM**
- Problème : risque de confondre conversions de campagnes et clients finaux.
- Solution : affichage séparé et note explicative dans le dashboard.
- Justification : éviter une décision budgétaire erronée.
        """
    )
