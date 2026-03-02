import pandas as pd
import streamlit as st

from src.app.services.geo_service import GeoService
from src.app.services.map_service import map_service
from src.data.mariadb_client import MariaDBClient


def _find_default_column(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {col.lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def _ip_candidates(columns: list[str]) -> list[str]:
    """Détecte les colonnes susceptibles de contenir des adresses IP."""
    keywords = ["ip", "addr", "src", "dst", "source", "dest"]
    hits: list[str] = []
    for col in columns:
        low = col.lower()
        if any(kw in low for kw in keywords):
            hits.append(col)
    return hits if hits else columns


# ── page setup ──────────────────────────────────────────────────────
st.set_page_config(page_title="Maps", layout="wide")

# Réduire la largeur de la sidebar
st.markdown(
    """<style>
    [data-testid="stSidebar"] { min-width: 180px; max-width: 220px; }
    </style>""",
    unsafe_allow_html=True,
)

st.header("🗺️ Cartographie des logs")
st.caption(
    "Les adresses IP sont géolocalisées via ip-api.com puis affichées sur une carte."
)

_TIME_COL = "datetime"  # colonne temporelle fixe

db_client = MariaDBClient()
maps = map_service()

if "geo" not in st.session_state:
    st.session_state["geo"] = GeoService()
geo: GeoService = st.session_state["geo"]

try:
    tables = db_client.list_tables()
    if not tables:
        st.warning("Aucune table disponible en base.")
        st.stop()

    default_table = "FW" if "FW" in tables else tables[0]

    # ── Sélecteurs principaux ───────────────────────────────────────
    col_a, col_b, col_c = st.columns([1.2, 1, 1])
    with col_a:
        selected_table = st.selectbox(
            "Table", options=tables, index=tables.index(default_table)
        )
    with col_b:
        map_type = st.selectbox(
            "Type de carte",
            options=["points", "choropleth"],
            index=0,
        )
    with col_c:
        # Nombre total de lignes dans la table
        count_df = db_client.execute_query(
            f"SELECT COUNT(*) AS total FROM {selected_table}"
        )
        max_rows = int(count_df.iloc[0]["total"]) if not count_df.empty else 20000
        default_rows = min(5000, max_rows)
        row_limit = st.slider(
            "Nombre de lignes",
            min_value=200,
            max_value=max(200, max_rows),
            value=default_rows,
            step=200,
        )

    table_columns = db_client.list_columns(selected_table)

    # ── Colonne IP à géolocaliser ───────────────────────────────────
    ip_cols = _ip_candidates(table_columns)
    default_ip = (
        _find_default_column(ip_cols, ["ipsrc", "ip_src", "src_ip", "source_ip"])
        or ip_cols[0]
    )
    ip_col = st.selectbox(
        "Colonne IP à géolocaliser",
        options=ip_cols,
        index=ip_cols.index(default_ip) if default_ip in ip_cols else 0,
    )

    # ── Filtre temporel (colonne fixe : datetime) ───────────────────
    time_where_clause = None
    time_params: dict = {}

    if _TIME_COL in table_columns:
        bounds_query = (
            f"SELECT MIN({_TIME_COL}) AS min_val, MAX({_TIME_COL}) AS max_val "
            f"FROM {selected_table} WHERE {_TIME_COL} IS NOT NULL"
        )
        bounds_df = db_client.execute_query(bounds_query)

        min_available = None
        max_available = None
        if not bounds_df.empty:
            min_raw = bounds_df.iloc[0]["min_val"]
            max_raw = bounds_df.iloc[0]["max_val"]
            if min_raw is not None and max_raw is not None:
                parsed_min = pd.to_datetime(min_raw, errors="coerce")
                parsed_max = pd.to_datetime(max_raw, errors="coerce")
                if not pd.isna(parsed_min) and not pd.isna(parsed_max):
                    min_available = parsed_min
                    max_available = parsed_max

        if min_available is not None and max_available is not None:
            st.caption(f"Plage disponible : {min_available} → {max_available}")
            if min_available == max_available:
                st.info("La base ne contient qu'un seul instant.")
                start_time, end_time = min_available, max_available
            else:
                start_time, end_time = st.slider(
                    "Plage temporelle",
                    min_value=min_available.to_pydatetime(),
                    max_value=max_available.to_pydatetime(),
                    value=(
                        min_available.to_pydatetime(),
                        max_available.to_pydatetime(),
                    ),
                    format="YYYY-MM-DD HH:mm:ss",
                )
            time_where_clause = f"{_TIME_COL} BETWEEN :start_time AND :end_time"
            time_params = {
                "start_time": pd.to_datetime(start_time),
                "end_time": pd.to_datetime(end_time),
            }

    _ACTION_COL = "action"
    _COMPUTED_METRICS = ["Nb requêtes", "Nb Permit", "Nb Deny"]

    # ── Carte points ────────────────────────────────────────────────
    if map_type == "points":
        opt1, opt2, opt3 = st.columns(3)
        with opt1:
            size_metric = st.selectbox(
                "Taille des points",
                options=["(aucun)"] + _COMPUTED_METRICS,
                index=1,
            )
        with opt2:
            color_metric = st.selectbox(
                "Couleur des points",
                options=["(aucun)", "Pays"] + _COMPUTED_METRICS,
                index=1,
            )
        with opt3:
            color_scale = st.selectbox(
                "Palette de couleurs",
                options=map_service.COLOR_SCALES,
                index=0,
            )
        log_scale = st.checkbox("Échelle logarithmique (taille)", value=False)

        # Colonnes à récupérer : IP + action
        required_cols = list({ip_col, _ACTION_COL} & set(table_columns))
        if ip_col not in required_cols:
            required_cols.insert(0, ip_col)
        if _ACTION_COL in table_columns and _ACTION_COL not in required_cols:
            required_cols.append(_ACTION_COL)

        df_raw = db_client.fetch_table(
            table_name=selected_table,
            columns=required_cols,
            where_clause=time_where_clause,
            params=time_params,
            limit=row_limit,
        )

        if df_raw.empty:
            st.warning("Aucune donnée pour les filtres sélectionnés.")
            st.stop()

        # ── Agrégation par IP : nb requêtes, nb permit, nb deny ─────
        if _ACTION_COL in df_raw.columns:
            agg_ip = (
                df_raw.groupby(ip_col)
                .agg(
                    **{
                        "Nb requêtes": (ip_col, "count"),
                        "Nb Permit": (
                            _ACTION_COL,
                            lambda s: (s.str.lower() == "permit").sum(),
                        ),
                        "Nb Deny": (
                            _ACTION_COL,
                            lambda s: (s.str.lower() == "deny").sum(),
                        ),
                    }
                )
                .reset_index()
            )
        else:
            agg_ip = df_raw.groupby(ip_col).size().reset_index(name="Nb requêtes")
            agg_ip["Nb Permit"] = 0
            agg_ip["Nb Deny"] = 0

        # ── Géolocalisation ──────────────────────────────────────────
        with st.spinner("Géolocalisation des adresses IP…"):
            df_geo = geo.enrich_dataframe(agg_ip, ip_col)

        if df_geo.empty:
            st.warning(
                "Aucune IP publique géolocalisée (IPs privées ou non résolvables)."
            )
            st.stop()

        st.caption(
            f"{len(df_geo)} IPs géolocalisées sur "
            f"{agg_ip[ip_col].nunique()} uniques "
            f"({len(df_raw)} lignes brutes)"
        )

        # ── Colonnes effectives ──────────────────────────────────────
        effective_size = None if size_metric == "(aucun)" else size_metric
        effective_color = (
            None
            if color_metric == "(aucun)"
            else "country"
            if color_metric == "Pays"
            else color_metric
        )

        # Hover riche
        hover_data_cols = list(
            dict.fromkeys(
                [ip_col, "country", "city", "region", "isp"] + _COMPUTED_METRICS
            )
        )
        hover_data_cols = [c for c in hover_data_cols if c in df_geo.columns]

        title_parts = []
        if size_metric != "(aucun)":
            title_parts.append(f"taille = {size_metric}")
        if color_metric != "(aucun)":
            title_parts.append(f"couleur = {color_metric}")
        suffix = f"  ({', '.join(title_parts)})" if title_parts else ""
        map_title = f"Carte – {ip_col}{suffix}"

        fig = maps.create_metric_bubble_map(
            df=df_geo,
            lat_col="lat",
            lon_col="lon",
            metric_col=effective_size,
            color_col=effective_color,
            hover_cols=hover_data_cols,
            title=map_title,
            log_scale=log_scale,
            color_continuous_scale=color_scale,
        )

    # ── Choroplèthe ─────────────────────────────────────────────────
    else:
        choro1, choro2 = st.columns(2)
        with choro1:
            choro_metric = st.selectbox(
                "Métrique",
                options=_COMPUTED_METRICS,
                index=0,
            )
        with choro2:
            choro_color_scale = st.selectbox(
                "Palette de couleurs",
                options=map_service.COLOR_SCALES,
                index=0,
            )

        # Colonnes à récupérer : IP + action
        required_cols = [ip_col]
        if _ACTION_COL in table_columns and _ACTION_COL not in required_cols:
            required_cols.append(_ACTION_COL)

        df_raw = db_client.fetch_table(
            table_name=selected_table,
            columns=required_cols,
            where_clause=time_where_clause,
            params=time_params,
            limit=row_limit,
        )

        if df_raw.empty:
            st.warning("Aucune donnée pour les filtres sélectionnés.")
            st.stop()

        with st.spinner("Géolocalisation des adresses IP…"):
            df_geo = geo.enrich_dataframe(df_raw, ip_col)

        if df_geo.empty:
            st.warning("Aucune IP publique géolocalisée.")
            st.stop()

        # Agrégation par pays
        if _ACTION_COL in df_geo.columns:
            agg_df = (
                df_geo.groupby("country")
                .agg(
                    **{
                        "Nb requêtes": (ip_col, "count"),
                        "Nb Permit": (
                            _ACTION_COL,
                            lambda s: (s.str.lower() == "permit").sum(),
                        ),
                        "Nb Deny": (
                            _ACTION_COL,
                            lambda s: (s.str.lower() == "deny").sum(),
                        ),
                    }
                )
                .reset_index()
            )
        else:
            agg_df = df_geo.groupby("country").size().reset_index(name="Nb requêtes")
            agg_df["Nb Permit"] = 0
            agg_df["Nb Deny"] = 0

        fig = maps.create_choropleth_map(
            df=agg_df,
            location_col="country",
            metric_col=choro_metric,
            location_mode="country names",
            title=f"Choroplèthe – {choro_metric} par pays",
            color_continuous_scale=choro_color_scale,
        )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Aperçu des données géolocalisées"):
        st.dataframe(df_geo.head(200))

except (ValueError, KeyError, TypeError) as exc:
    st.error(f"Erreur : {exc}")
