import pandas as pd

from xgboost import XGBClassifier
from fraudshield.config import MODEL_CONFIG

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)


def build_model(y_train: pd.Series) -> XGBClassifier:
    """
    Cria o XGBoost com os melhores hiperparâmetros
    encontrados nos experimentos.
    """

    negative_count = (y_train == 0).sum()
    positive_count = (y_train == 1).sum()

    if positive_count == 0:
        raise ValueError(
            "O conjunto de treinamento não possui fraudes."
        )

    scale_pos_weight = negative_count / positive_count

    
    model = XGBClassifier(
        n_estimators=MODEL_CONFIG.n_estimators,
        max_depth=MODEL_CONFIG.max_depth,
        learning_rate=MODEL_CONFIG.learning_rate,
        subsample=MODEL_CONFIG.subsample,
        colsample_bytree=MODEL_CONFIG.colsample_bytree,
        min_child_weight=MODEL_CONFIG.min_child_weight,
        scale_pos_weight=scale_pos_weight,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=MODEL_CONFIG.random_state,
        n_jobs=-1
    )


    return model


def train_model(
    model: XGBClassifier,
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> XGBClassifier:
    """
    Treina o modelo com os dados fornecidos.
    """

    model.fit(X_train, y_train)

    return model


def evaluate_model(
    model: XGBClassifier,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> dict:
    """
    Avalia o modelo no conjunto de validação.
    """

    predictions = model.predict(X_val)
    probabilities = model.predict_proba(X_val)[:, 1]

    average_precision = average_precision_score(
        y_val,
        probabilities
    )

    roc_auc = roc_auc_score(
        y_val,
        probabilities
    )

    print("\n=== CLASSIFICATION REPORT ===")

    print(classification_report(
        y_val,
        predictions,
        digits=4,
        zero_division=0
    ))

    print("\nAverage Precision:", round(average_precision, 4))
    print("ROC-AUC:", round(roc_auc, 4))

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_val, predictions))

    return {
        "average_precision": average_precision,
        "roc_auc": roc_auc
    }