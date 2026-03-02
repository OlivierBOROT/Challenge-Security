# -*- coding: utf-8 -*-
"""
Service de visualisation pour l'application d'analyse de logs.
Génère des graphiques et visualisations interactives avec Streamlit, Plotly et autres.
"""

import logging
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class VisualizationService:
    """Service de génération de visualisations pour les logs de sécurité."""

    def __init__(self):
        self.color_schemes = {
            "security": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"],
            "traffic": ["#FF9999", "#66B2FF", "#99FF99", "#FFD700", "#FF69B4"],
            "protocols": {
                "TCP": "#FF6B6B",
                "UDP": "#4ECDC4",
                "ICMP": "#45B7D1",
                "Other": "#96CEB4",
            },
            "actions": {
                "DENY": "#FF4444",
                "ALLOW": "#44FF44",
                "DROP": "#FF8800",
                "ACCEPT": "#00FF88",
            },
        }

    def create_protocol_distribution_chart(
        self, df: pd.DataFrame, to_html: bool = False
    ) -> Union[go.Figure, str]:
        """Crée un graphique de distribution des protocoles."""
        try:
            if "protocol_deduced" not in df.columns:
                empty_chart = self._create_empty_chart(
                    "Données de protocole non disponibles"
                )
                return self._format_output(empty_chart, to_html)

            protocol_counts = df["protocol_deduced"].value_counts()

            # Graphique en secteurs avec barres
            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=("Distribution des Protocoles", "Volume par Protocole"),
                specs=[[{"type": "pie"}, {"type": "bar"}]],
            )

            self._add_protocol_pie_chart(fig, protocol_counts)
            self._add_protocol_bar_chart(fig, protocol_counts)

            fig.update_layout(
                title_text="Analyse des Protocoles Réseau", height=500, showlegend=False
            )

            return self._format_output(fig, to_html)

        except Exception as e:
            logger.error(f"Erreur création graphique protocoles: {e}")
            empty_chart = self._create_empty_chart(f"Erreur: {str(e)}")
            return self._format_output(empty_chart, to_html)

    def create_temporal_activity_chart(
        self, df: pd.DataFrame, to_html: bool = False
    ) -> Union[go.Figure, str]:
        """Crée un graphique d'activité temporelle."""
        try:
            if "timestamp" not in df.columns or df["timestamp"].isna().all():
                empty_chart = self._create_empty_chart(
                    "Données temporelles non disponibles"
                )
                return empty_chart.to_html() if to_html else empty_chart

            # Préparation des données temporelles
            df["hour"] = df["timestamp"].dt.hour
            df["date"] = df["timestamp"].dt.date

            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Activité par Heure",
                    "Activité par Jour",
                    "Heatmap Heure x Action",
                    "Tendance sur 24h",
                ),
                specs=[
                    [{"type": "bar"}, {"type": "scatter"}],
                    [{"type": "heatmap"}, {"type": "scatter"}],
                ],
            )

            hourly_activity = df["hour"].value_counts().sort_index()
            self._add_hourly_activity_chart(fig, hourly_activity)

            daily_activity = df.groupby("date").size().reset_index(name="count")
            self._add_daily_activity_chart(fig, daily_activity)

            if "action" in df.columns:
                hourly_actions = (
                    df.groupby(["hour", "action"]).size().unstack(fill_value=0)
                )
                self._add_hour_action_heatmap(fig, hourly_actions)

            if len(hourly_activity) >= 24:
                self._add_hourly_trend_chart(fig, hourly_activity)

            fig.update_layout(
                title_text="Analyse Temporelle de l'Activité Réseau",
                height=800,
                showlegend=True,
            )

            return self._format_output(fig, to_html)

        except Exception as e:
            logger.error(f"Erreur création graphique temporel: {e}")
            empty_chart = self._create_empty_chart(f"Erreur: {str(e)}")
            return self._format_output(empty_chart, to_html)

    def _add_protocol_pie_chart(
        self, fig: go.Figure, protocol_counts: pd.Series
    ) -> None:
        fig.add_trace(
            go.Pie(
                labels=protocol_counts.index,
                values=protocol_counts.values,
                hole=0.3,
                marker_colors=[
                    self.color_schemes["protocols"].get(p, "#CCCCCC")
                    for p in protocol_counts.index
                ],
            ),
            row=1,
            col=1,
        )

    def _add_protocol_bar_chart(
        self, fig: go.Figure, protocol_counts: pd.Series
    ) -> None:
        fig.add_trace(
            go.Bar(
                x=protocol_counts.index,
                y=protocol_counts.values,
                marker_color=[
                    self.color_schemes["protocols"].get(p, "#CCCCCC")
                    for p in protocol_counts.index
                ],
                text=[f"{v:,}" for v in protocol_counts.values],
                textposition="auto",
            ),
            row=1,
            col=2,
        )

    def _add_hourly_activity_chart(
        self, fig: go.Figure, hourly_activity: pd.Series
    ) -> None:
        fig.add_trace(
            go.Bar(
                x=hourly_activity.index,
                y=hourly_activity.values,
                marker_color="lightblue",
                name="Connexions/Heure",
            ),
            row=1,
            col=1,
        )

    def _add_daily_activity_chart(
        self, fig: go.Figure, daily_activity: pd.DataFrame
    ) -> None:
        fig.add_trace(
            go.Scatter(
                x=daily_activity["date"],
                y=daily_activity["count"],
                mode="lines+markers",
                marker_color="orange",
                name="Activité quotidienne",
            ),
            row=1,
            col=2,
        )

    def _add_hour_action_heatmap(
        self, fig: go.Figure, hourly_actions: pd.DataFrame
    ) -> None:
        fig.add_trace(
            go.Heatmap(
                z=hourly_actions.values.T,
                x=hourly_actions.index,
                y=hourly_actions.columns,
                colorscale="Reds",
                name="Actions par heure",
            ),
            row=2,
            col=1,
        )

    def _add_hourly_trend_chart(
        self, fig: go.Figure, hourly_activity: pd.Series
    ) -> None:
        moving_avg = hourly_activity.rolling(window=3, center=True).mean()
        fig.add_trace(
            go.Scatter(
                x=hourly_activity.index,
                y=moving_avg,
                mode="lines",
                marker_color="red",
                name="Moyenne mobile",
                line=dict(width=3),
            ),
            row=2,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=hourly_activity.index,
                y=hourly_activity.values,
                mode="markers",
                marker_color="lightgray",
                name="Données brutes",
                opacity=0.6,
            ),
            row=2,
            col=2,
        )

    def create_security_dashboard(
        self, df: pd.DataFrame, stats: Dict[str, Any], to_html: bool = False
    ) -> Union[go.Figure, str]:
        """Crée un tableau de bord de sécurité."""
        try:
            fig = make_subplots(
                rows=3,
                cols=2,
                subplot_titles=(
                    "Actions de Sécurité",
                    "Top 10 IPs Sources",
                    "Top 10 Ports Ciblés",
                    "Règles les Plus Utilisées",
                    "Ratio DENY/ALLOW par Heure",
                    "Géolocalisation (Simulation)",
                ),
                specs=[
                    [{"type": "pie"}, {"type": "bar"}],
                    [{"type": "bar"}, {"type": "bar"}],
                    [{"type": "scatter"}, {"type": "scatter"}],
                ],
            )

            self._add_security_actions_pie(fig, stats)
            self._add_top_source_ips_bar(fig, stats)
            self._add_top_ports_bar(fig, stats)
            self._add_top_rules_bar(fig, stats)
            self._add_deny_allow_ratio_line(fig, df)
            self._add_geo_simulation_scatter(fig)

            fig.update_layout(
                title_text="Tableau de Bord Sécurité", height=1200, showlegend=False
            )

            return self._format_output(fig, to_html)

        except Exception as e:
            logger.error(f"Erreur création dashboard sécurité: {e}")
            empty_chart = self._create_empty_chart(f"Erreur: {str(e)}")
            return self._format_output(empty_chart, to_html)

    def _add_security_actions_pie(self, fig: go.Figure, stats: Dict[str, Any]) -> None:
        if "action_distribution" not in stats or not stats["action_distribution"]:
            return

        actions = list(stats["action_distribution"].keys())
        counts = list(stats["action_distribution"].values())
        colors = [
            self.color_schemes["actions"].get(action, "#CCCCCC") for action in actions
        ]

        fig.add_trace(
            go.Pie(labels=actions, values=counts, marker_colors=colors, hole=0.4),
            row=1,
            col=1,
        )

    def _add_top_source_ips_bar(self, fig: go.Figure, stats: Dict[str, Any]) -> None:
        if "top_src_ips" not in stats or not stats["top_src_ips"]:
            return

        ips = list(stats["top_src_ips"].keys())[:10]
        counts = list(stats["top_src_ips"].values())[:10]

        fig.add_trace(
            go.Bar(
                y=ips,
                x=counts,
                orientation="h",
                marker_color="crimson",
                text=[f"{c:,}" for c in counts],
                textposition="inside",
            ),
            row=1,
            col=2,
        )

    def _add_top_ports_bar(self, fig: go.Figure, stats: Dict[str, Any]) -> None:
        if "top_ports" not in stats or not stats["top_ports"]:
            return

        ports = list(stats["top_ports"].keys())[:10]
        port_counts = list(stats["top_ports"].values())[:10]

        fig.add_trace(
            go.Bar(
                x=[str(p) for p in ports],
                y=port_counts,
                marker_color="steelblue",
                text=[f"{c:,}" for c in port_counts],
                textposition="auto",
            ),
            row=2,
            col=1,
        )

    def _add_top_rules_bar(self, fig: go.Figure, stats: Dict[str, Any]) -> None:
        if "top_rules" not in stats or not stats["top_rules"]:
            return

        rules = list(stats["top_rules"].keys())[:10]
        rule_counts = list(stats["top_rules"].values())[:10]

        fig.add_trace(
            go.Bar(
                x=[f"R{r}" for r in rules],
                y=rule_counts,
                marker_color="goldenrod",
                text=[f"{c:,}" for c in rule_counts],
                textposition="auto",
            ),
            row=2,
            col=2,
        )

    def _add_deny_allow_ratio_line(self, fig: go.Figure, df: pd.DataFrame) -> None:
        if "hour" not in df.columns or "action" not in df.columns:
            return

        hourly_actions = df.groupby(["hour", "action"]).size().unstack(fill_value=0)
        if (
            "DENY" not in hourly_actions.columns
            or "ALLOW" not in hourly_actions.columns
        ):
            return

        deny_ratio = (
            hourly_actions["DENY"]
            / (hourly_actions["DENY"] + hourly_actions["ALLOW"])
            * 100
        )

        fig.add_trace(
            go.Scatter(
                x=deny_ratio.index,
                y=deny_ratio.values,
                mode="lines+markers",
                marker_color="red",
                name="% DENY",
                line=dict(width=3),
            ),
            row=3,
            col=1,
        )

    def _add_geo_simulation_scatter(self, fig: go.Figure) -> None:
        sample_countries = ["USA", "China", "Russia", "Brazil", "Germany"]
        sample_attacks = np.random.default_rng().integers(
            100, 5000, len(sample_countries)
        )

        fig.add_trace(
            go.Scatter(
                x=sample_countries,
                y=sample_attacks,
                mode="markers",
                marker=dict(
                    size=sample_attacks / 100,
                    color=sample_attacks,
                    colorscale="Reds",
                    showscale=True,
                    colorbar=dict(title="Niveau d'attaque"),
                ),
                text=[
                    f"{country}: {attacks} attaques"
                    for country, attacks in zip(sample_countries, sample_attacks)
                ],
                name="Activité par pays",
            ),
            row=3,
            col=2,
        )

    def create_anomaly_detection_chart(
        self,
        df: pd.DataFrame,
        anomaly_data: Dict[str, Any],
        threshold: float = 5.0,
        to_html: bool = False,
    ) -> Union[go.Figure, str]:
        """Crée des graphiques de détection d'anomalies."""
        try:
            _ = df
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Scores d'Anomalies dans le Temps",
                    "Distribution des Scores",
                    "Anomalies Détectées",
                    "Seuil vs Prédictions",
                ),
                specs=[
                    [{"type": "scatter"}, {"type": "histogram"}],
                    [{"type": "scatter"}, {"type": "bar"}],
                ],
            )

            timestamps = anomaly_data.get("timestamps", [])
            scores = anomaly_data.get("anomaly_scores", [])
            predictions = anomaly_data.get("predictions", [])
            threshold_val = anomaly_data.get("threshold", threshold)

            self._add_anomaly_scores_scatter(fig, timestamps, scores, threshold_val)
            self._add_anomaly_distribution_histogram(fig, scores)
            self._add_detected_anomalies_scatter(fig, timestamps, scores, predictions)
            self._add_anomaly_classification_bar(fig, scores, predictions)

            fig.update_layout(
                title_text="Détection d'Anomalies de Sécurité",
                height=800,
                showlegend=True,
            )

            return self._format_output(fig, to_html)

        except Exception as e:
            logger.error(f"Erreur création graphique anomalies: {e}")
            empty_chart = self._create_empty_chart(f"Erreur: {str(e)}")
            return self._format_output(empty_chart, to_html)

    def _add_anomaly_scores_scatter(
        self,
        fig: go.Figure,
        timestamps: List[Any],
        scores: List[float],
        threshold_val: float,
    ) -> None:
        if not timestamps or not scores:
            return

        colors = ["red" if score > threshold_val else "blue" for score in scores]
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=scores,
                mode="markers",
                marker=dict(color=colors, size=6),
                name="Scores d'anomalie",
            ),
            row=1,
            col=1,
        )

    def _add_anomaly_distribution_histogram(
        self, fig: go.Figure, scores: List[float]
    ) -> None:
        if not scores:
            return

        fig.add_trace(
            go.Histogram(
                x=scores,
                nbinsx=30,
                marker_color="lightblue",
                opacity=0.7,
                name="Distribution",
            ),
            row=1,
            col=2,
        )

    def _add_detected_anomalies_scatter(
        self,
        fig: go.Figure,
        timestamps: List[Any],
        scores: List[float],
        predictions: List[int],
    ) -> None:
        if not timestamps or not scores or not predictions:
            return

        anomaly_times = [
            timestamps[i] for i, pred in enumerate(predictions) if pred == 1
        ]
        anomaly_scores = [scores[i] for i, pred in enumerate(predictions) if pred == 1]

        fig.add_trace(
            go.Scatter(
                x=anomaly_times,
                y=anomaly_scores,
                mode="markers",
                marker=dict(color="red", size=10, symbol="triangle-up"),
                name="Anomalies détectées",
            ),
            row=2,
            col=1,
        )

    def _add_anomaly_classification_bar(
        self, fig: go.Figure, scores: List[float], predictions: List[int]
    ) -> None:
        if not scores or not predictions:
            return

        predicted_anomalies = sum(predictions)
        normal_events = len(scores) - predicted_anomalies
        categories = ["Normal", "Anomalies"]
        values = [normal_events, predicted_anomalies]

        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                marker_color=["green", "red"],
                name="Classification",
                text=[f"{v}" for v in values],
                textposition="auto",
            ),
            row=2,
            col=2,
        )

    def create_network_topology_chart(
        self, df: pd.DataFrame, max_nodes: int = 50, to_html: bool = False
    ) -> Union[go.Figure, str]:
        """Crée une visualisation de topologie réseau."""
        try:
            # Prendre un échantillon pour éviter la surcharge
            sample_df = df.sample(n=min(len(df), 1000)) if len(df) > 1000 else df

            # Créer les connexions source -> destination
            connections = (
                sample_df.groupby(["source_ip", "destination_ip"])
                .size()
                .reset_index(name="weight")
            )
            connections = connections.nlargest(max_nodes, "weight")

            # Créer les noeuds
            all_ips = pd.concat(
                [connections["source_ip"], connections["destination_ip"]]
            ).unique()

            # Positions en cercle pour simplifier
            import math

            positions = {}
            n_nodes = len(all_ips)
            for i, ip in enumerate(all_ips):
                angle = 2 * math.pi * i / n_nodes
                positions[ip] = (math.cos(angle), math.sin(angle))

            # Créer les traces pour les liens
            edge_traces = []
            for _, row in connections.iterrows():
                src_ip, dst_ip = row["source_ip"], row["destination_ip"]
                src_pos = positions[src_ip]
                dst_pos = positions[dst_ip]

                edge_traces.append(
                    go.Scatter(
                        x=[src_pos[0], dst_pos[0], None],
                        y=[src_pos[1], dst_pos[1], None],
                        mode="lines",
                        line=dict(width=1, color="lightgray"),
                        hoverinfo="none",
                        showlegend=False,
                    )
                )

            # Tracer les noeuds
            node_trace = go.Scatter(
                x=[positions[ip][0] for ip in all_ips],
                y=[positions[ip][1] for ip in all_ips],
                mode="markers+text",
                marker=dict(
                    size=10, color="lightblue", line=dict(width=1, color="navy")
                ),
                text=[
                    ip.split(".")[-1] for ip in all_ips
                ],  # Afficher seulement le dernier octet
                textposition="middle center",
                hovertext=[f"IP: {ip}" for ip in all_ips],
                hoverinfo="text",
                name="Noeuds réseau",
            )

            fig = go.Figure(data=edge_traces + [node_trace])
            fig.update_layout(
                title="Topologie Réseau (Échantillon)",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="Visualisation simplifiée des connexions réseau",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.005,
                        y=-0.002,
                        xanchor="left",
                        yanchor="bottom",
                        font=dict(color="gray", size=12),
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600,
            )

            return self._format_output(fig, to_html)

        except Exception as e:
            logger.error(f"Erreur création graphique topologie: {e}")
            empty_chart = self._create_empty_chart(f"Erreur: {str(e)}")
            return self._format_output(empty_chart, to_html)

    def _format_output(self, fig: go.Figure, to_html: bool) -> Union[go.Figure, str]:
        """Retourne soit la figure Plotly soit son HTML."""
        return fig.to_html() if to_html else fig

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Crée un graphique vide avec un message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(visible=False), yaxis=dict(visible=False), height=400
        )
        return fig

    def display_metrics_cards(self, stats: Dict[str, Any]) -> None:
        """Affiche les métriques sous forme de cartes Streamlit."""
        try:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_logs = stats.get("total_logs", 0)
                st.metric("Logs Totaux", f"{total_logs:,}")

            with col2:
                deny_count = stats.get("action_distribution", {}).get("DENY", 0)
                allow_count = stats.get("action_distribution", {}).get("ALLOW", 0)
                deny_ratio = (
                    (deny_count / (deny_count + allow_count) * 100)
                    if (deny_count + allow_count) > 0
                    else 0
                )
                st.metric(
                    "Taux de Blocage", f"{deny_ratio:.1f}%", f"{deny_count:,} DENY"
                )

            with col3:
                unique_ips = stats.get("unique_src_ips", 0)
                st.metric("IPs Sources Uniques", f"{unique_ips:,}")

            with col4:
                protocols = len(stats.get("protocol_distribution", {}))
                st.metric("Protocoles Détectés", protocols)

        except Exception as e:
            logger.error(f"Erreur affichage métriques: {e}")
            st.error(f"Erreur lors de l'affichage des métriques: {e}")

    def create_interactive_filter_sidebar(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Crée une sidebar interactive avec des filtres."""
        st.sidebar.header("🔍 Filtres d'Analyse")

        filters = {}

        try:
            # Filtre par date
            if "timestamp" in df.columns and not df["timestamp"].isna().all():
                date_range = st.sidebar.date_input(
                    "Période d'analyse",
                    value=(df["timestamp"].min().date(), df["timestamp"].max().date()),
                    min_value=df["timestamp"].min().date(),
                    max_value=df["timestamp"].max().date(),
                )
                filters["date_range"] = date_range

            # Filtre par protocole
            if "protocol_deduced" in df.columns:
                protocols = st.sidebar.multiselect(
                    "Protocoles",
                    options=df["protocol_deduced"].unique(),
                    default=df["protocol_deduced"].unique(),
                )
                filters["protocols"] = protocols

            # Filtre par action
            if "action" in df.columns:
                actions = st.sidebar.multiselect(
                    "Actions",
                    options=df["action"].unique(),
                    default=df["action"].unique(),
                )
                filters["actions"] = actions

            # Filtre par plage d'heure
            if "hour" in df.columns:
                hour_range = st.sidebar.slider("Plage horaire", 0, 23, (0, 23))
                filters["hour_range"] = hour_range

            # Filtre par top N
            top_n = st.sidebar.number_input(
                "Top N éléments à afficher", min_value=5, max_value=100, value=20
            )
            filters["top_n"] = top_n

        except Exception as e:
            logger.error(f"Erreur création filtres: {e}")
            st.sidebar.error(f"Erreur lors de la création des filtres: {e}")

        return filters
