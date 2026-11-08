
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
)



# METRICAS DE INFERENCIA


TRANSACTIONS_PROCESSED = Counter(
    "fraudshield_transactions_processed_total",
    "Total de transacoes processadas com sucesso.",
)

PREDICTIONS_TOTAL = Counter(
    "fraudshield_predictions_total",
    "Total de previsoes por classificacao.",
    labelnames=["prediction"],
)

INFERENCE_DURATION = Histogram(
    "fraudshield_inference_duration_seconds",
    "Tempo de execucao da inferencia em segundos.",
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
)

INFERENCE_ERRORS = Counter(
    "fraudshield_inference_errors_total",
    "Total de erros durante a inferencia.",
)

INFERENCE_IN_PROGRESS = Gauge(
    "fraudshield_inference_in_progress",
    "Numero de inferencias em andamento.",
)



# METRICAS DE DATA DRIFT


DATA_DRIFT_PSI = Gauge(
    "fraudshield_data_drift_psi",
    "PSI calculado por feature.",
    labelnames=["feature"],
)

DATA_DRIFT_SIGNIFICANT_FEATURES = Gauge(
    "fraudshield_data_drift_significant_features",
    "Quantidade de features com drift significativo.",
)

DATA_DRIFT_MODERATE_FEATURES = Gauge(
    "fraudshield_data_drift_moderate_features",
    "Quantidade de features com drift moderado.",
)

DATA_DRIFT_SAMPLE_SIZE = Gauge(
    "fraudshield_data_drift_sample_size",
    "Quantidade de transacoes utilizadas na analise.",
)

DATA_DRIFT_ANALYSIS_STATUS = Gauge(
    "fraudshield_data_drift_analysis_status",
    "Estado da ultima analise: 1 analisado, 0 insuficiente.",
)

DATA_DRIFT_LAST_ANALYSIS_TIMESTAMP = Gauge(
    "fraudshield_data_drift_last_analysis_timestamp_seconds",
    "Timestamp Unix da ultima analise de drift publicada.",
)
