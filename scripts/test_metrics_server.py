
import time

from fraudshield.monitoring.server import (
    start_metrics_server,
)
from fraudshield.monitoring.service import (
    MonitoringService,
)


def main():
    print("\n=== FRAUDSHIELD METRICS TEST ===")

    start_metrics_server(port=8001)

    monitoring = MonitoringService()

    # Gerar metricas de exemplo.
    for _ in range(5):
        with monitoring.track_inference():
            time.sleep(0.02)

        monitoring.record_prediction(0)

    for _ in range(2):
        with monitoring.track_inference():
            time.sleep(0.03)

        monitoring.record_prediction(1)

    print("\nMetricas registradas!")
    print("Transacoes processadas: 7")
    print("Legitimas: 5")
    print("Fraudes previstas: 2")

    print("\nEndpoint disponivel:")
    print("http://localhost:8001/metrics")

    print("\nPressione Ctrl+C para encerrar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
