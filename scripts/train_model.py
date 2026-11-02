
from pathlib import Path
from fraudshield.config import MODEL_CONFIG

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)

from fraudshield.training import (
    build_model,
    train_model,
    evaluate_model
)

from fraudshield.model_io import save_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "creditcard.csv"
)

MODEL_PATH = MODEL_CONFIG.model_path


def main():
    print("=== FRAUDSHIELD AI — TREINAMENTO ===")

    # 1. Carregar dataset
    print("\n[1/5] Carregando dataset...")

    df = load_dataset(DATA_PATH)

    X, y = split_features_target(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(X, y)

    print(f"Treino: {len(X_train)} transações")
    print(f"Validação: {len(X_val)} transações")
    print(f"Teste reservado: {len(X_test)} transações")

    # 2. Criar modelo
    print("\n[2/5] Criando modelo...")

    model = build_model(y_train)

    print(model)

    # 3. Treinar modelo
    print("\n[3/5] Treinando XGBoost...")

    model = train_model(
        model,
        X_train,
        y_train
    )

    print("Treinamento concluído!")

    # 4. Avaliar na validação
    print("\n[4/5] Avaliando modelo...")

    metrics = evaluate_model(
        model,
        X_val,
        y_val
    )

    print("\n=== RESUMO ===")
    print(
        f"Average Precision: "
        f"{metrics['average_precision']:.4f}"
    )
    print(
        f"ROC-AUC: "
        f"{metrics['roc_auc']:.4f}"
    )

    # 5. Salvar modelo
    print("\n[5/5] Salvando modelo...")

    save_model(model, MODEL_PATH)

    print("\n=== TREINAMENTO FINALIZADO ===")
    print("Pipeline executado com sucesso!")
    print(f"Modelo disponível em: {MODEL_PATH}")


if __name__ == "__main__":
    main()
