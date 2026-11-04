
import torch
from torch import nn


class FraudMLP(nn.Module):
    """
    Rede neural MLP para classificação binária
    de transações financeiras.

    Entrada: 30 features numéricas.
    Saída: 1 logit por transação.
    """

    def __init__(
        self,
        input_dim: int = 30,
        dropout: float = 0.3,
    ):
        super().__init__()

        if input_dim <= 0:
            raise ValueError(
                "input_dim deve ser positivo."
            )

        if not 0 <= dropout < 1:
            raise ValueError(
                "dropout deve estar entre 0 e 1."
            )

        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(p=dropout),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(p=0.2),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, 1),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        """
        Retorna os logits da classificação.
        """
        return self.network(x)

    @torch.no_grad()
    def predict_proba(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        """
        Retorna a probabilidade estimada de fraude.
        """
        self.eval()

        logits = self.forward(x)

        return torch.sigmoid(logits)
