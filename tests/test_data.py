
import pandas as pd
import pytest

from fraudshield.data import (
    load_dataset,
    split_features_target,
    split_dataset
)


@pytest.fixture
def sample_dataset():
    """
    Cria um pequeno dataset fictício
    para testar nossas funções.
    """

    return pd.DataFrame({
        "V1": [float(i) for i in range(100)],
        "V2": [float(i * 2) for i in range(100)],
        "Amount": [100.0 + i for i in range(100)],
        "Class": [0] * 80 + [1] * 20
    })


def test_load_dataset_success(tmp_path, sample_dataset):
    file_path = tmp_path / "transactions.csv"

    sample_dataset.to_csv(file_path, index=False)

    result = load_dataset(file_path)

    assert len(result) == 100
    assert "Class" in result.columns
    assert list(result.columns) == list(sample_dataset.columns)


def test_load_dataset_file_not_found(tmp_path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_dataset(file_path)


def test_load_dataset_empty_file(tmp_path):
    file_path = tmp_path / "empty.csv"

    pd.DataFrame(columns=["V1", "Class"]).to_csv(
        file_path,
        index=False
    )

    with pytest.raises(ValueError):
        load_dataset(file_path)


def test_load_dataset_missing_target(tmp_path):
    file_path = tmp_path / "missing_target.csv"

    pd.DataFrame({
        "V1": [1.0, 2.0],
        "Amount": [100.0, 200.0]
    }).to_csv(file_path, index=False)

    with pytest.raises(ValueError):
        load_dataset(file_path)


def test_split_features_target(sample_dataset):
    X, y = split_features_target(sample_dataset)

    assert "Class" not in X.columns
    assert X.shape == (100, 3)
    assert len(y) == 100
    assert y.sum() == 20


def test_split_dataset_sizes(sample_dataset):
    X, y = split_features_target(sample_dataset)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(X, y)

    assert len(X_train) == 70
    assert len(X_val) == 15
    assert len(X_test) == 15

    assert len(y_train) == 70
    assert len(y_val) == 15
    assert len(y_test) == 15


def test_split_dataset_no_overlap(sample_dataset):
    X, y = split_features_target(sample_dataset)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_dataset(X, y)

    train_indices = set(X_train.index)
    val_indices = set(X_val.index)
    test_indices = set(X_test.index)

    assert train_indices.isdisjoint(val_indices)
    assert train_indices.isdisjoint(test_indices)
    assert val_indices.isdisjoint(test_indices)

    assert len(
        train_indices | val_indices | test_indices
    ) == len(sample_dataset)


def test_split_dataset_reproducibility(sample_dataset):
    X, y = split_features_target(sample_dataset)

    first_split = split_dataset(
        X, y, random_state=42
    )

    second_split = split_dataset(
        X, y, random_state=42
    )

    for first, second in zip(first_split, second_split):

        if isinstance(first, pd.DataFrame):
            pd.testing.assert_frame_equal(
                first,
                second
            )

        elif isinstance(first, pd.Series):
            pd.testing.assert_series_equal(
                first,
                second
            )
