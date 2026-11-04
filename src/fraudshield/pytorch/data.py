
from dataclasses import dataclass

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset,
)


@dataclass
class PreparedData:
    train_loader: DataLoader
    val_loader: DataLoader
    test_loader: DataLoader
    scaler: StandardScaler
    input_dim: int
    positive_count: int
    negative_count: int


def prepare_pytorch_data(
    dataset_path: str = "data/raw/creditcard.csv",
    batch_size: int = 512,
    random_state: int = 42,
) -> PreparedData:
    """
    Prepara os dados para treinamento de uma MLP.

    O scaler é ajustado somente no treino,
    evitando vazamento de informações.
    """

    if batch_size <= 0:
        raise ValueError("batch_size deve ser positivo.")

    df = load_dataset(dataset_path)
    X, y = split_features_target(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(
        X,
        y,
        random_state=random_state,
    )

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    def make_dataset(features, labels):
        features_tensor = torch.from_numpy(
            np.asarray(features, dtype=np.float32)
        )

        labels_tensor = torch.from_numpy(
            labels.to_numpy(dtype=np.float32)
        ).unsqueeze(1)

        return TensorDataset(
            features_tensor,
            labels_tensor,
        )

    train_dataset = make_dataset(
        X_train_scaled,
        y_train,
    )

    val_dataset = make_dataset(
        X_val_scaled,
        y_val,
    )

    test_dataset = make_dataset(
        X_test_scaled,
        y_test,
    )

    generator = torch.Generator().manual_seed(
        random_state
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    positive_count = int((y_train == 1).sum())
    negative_count = int((y_train == 0).sum())

    if positive_count == 0:
        raise ValueError(
            "O conjunto de treino não possui fraudes."
        )

    return PreparedData(
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        scaler=scaler,
        input_dim=X_train.shape[1],
        positive_count=positive_count,
        negative_count=negative_count,
    )
