
from pathlib import Path
import json

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    brier_score_loss
)

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)

from fraudshield.model_io import load_model
from fraudshield.inference import predict_fraud
from fraudshield.config import MODEL_CONFIG


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "experiments"
    / "final_evaluation.json"
)


def main():
    print("=== FRAUDSHIELD AI — AVALIAÇÃO FINAL ===")

    print("\n[1/4] Carregando dataset...")

    df = load_dataset(DATA_PATH)
    X, y = split_features_target(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(
        X,
        y,
        random_state=MODEL_CONFIG.random_state
    )

    print(f"Transações de teste: {len(X_test)}")
    print(f"Fraudes reais: {int(y_test.sum())}")

    print("\n[2/4] Carregando modelo salvo...")

    model = load_model(MODEL_CONFIG.model_path)

    print(f"Modelo: {MODEL_CONFIG.model_name}")
    print(f"Versão: {MODEL_CONFIG.model_version}")
    print(f"Threshold: {MODEL_CONFIG.threshold}")

    print("\n[3/4] Realizando previsões...")

    results = predict_fraud(
        model=model,
        transactions=X_test,
        threshold=MODEL_CONFIG.threshold
    )

    y_pred = results["prediction"]
    y_proba = results["fraud_score"]

    metrics = {
        "model_name": MODEL_CONFIG.model_name,
        "model_version": MODEL_CONFIG.model_version,
        "threshold": MODEL_CONFIG.threshold,
        "test_samples": int(len(X_test)),
        "test_frauds": int(y_test.sum()),
        "precision": float(
            precision_score(y_test, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, y_pred, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, y_pred, zero_division=0)
        ),
        "average_precision": float(
            average_precision_score(y_test, y_proba)
        ),
        "roc_auc": float(
            roc_auc_score(y_test, y_proba)
        ),
        "brier_score": float(
            brier_score_loss(y_test, y_proba)
        )
    }

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    ).ravel()

    metrics["confusion_matrix"] = {
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp)
    }

    print("\n=== CLASSIFICATION REPORT ===")
    print(
        classification_report(
            y_test,
            y_pred,
            digits=4,
            zero_division=0
        )
    )

    print("\n=== MÉTRICAS FINAIS ===")

    for metric in [
        "precision",
        "recall",
        "f1_score",
        "average_precision",
        "roc_auc",
        "brier_score"
    ]:
        print(f"{metric}: {metrics[metric]:.6f}")

    print("\nMatriz de confusão:")
    print([[tn, fp], [fn, tp]])

    print("\n[4/4] Salvando resultados...")

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            metrics,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Resultados salvos em: {RESULTS_PATH}")

    print("\nAvaliação final concluída!")


if __name__ == "__main__":
    main()
