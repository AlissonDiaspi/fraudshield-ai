from pathlib import Path

from xgboost import XGBClassifier


def save_model(
    model: XGBClassifier,
    file_path: str | Path
) -> None:
    """
    Salva o modelo XGBoost treinado.
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model.save_model(str(file_path))

    print(f"Modelo salvo em: {file_path}")


def load_model(
    file_path: str | Path
) -> XGBClassifier:
    """
    Carrega um modelo XGBoost salvo.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado: {file_path}"
        )

    model = XGBClassifier()

    model.load_model(str(file_path))

    return model