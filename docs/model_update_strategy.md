
# FraudShield AI — Model Update Strategy

## 1. Objetivo

Definir uma estratégia segura para identificar mudanças
na distribuição dos dados e avaliar a necessidade
de atualizar o modelo de detecção de fraudes.

## 2. Monitoramento

O FraudShield AI utiliza:

- Prometheus para coleta de métricas.
- Grafana para visualização.
- Population Stability Index (PSI) para Data Drift.
- MLflow para versionamento e registro de modelos.
- PostgreSQL para persistência das previsões.

## 3. Referência estatística

O baseline é construído utilizando exclusivamente
os dados de treinamento.

Arquivo:

`artifacts/monitoring/drift_baseline.json`

As distribuições recentes são comparadas com
os intervalos fixos definidos nesse baseline.

## 4. Classificação do PSI

| PSI | Classificação |
|---|---|
| < 0.10 | STABLE |
| 0.10 a < 0.25 | MODERATE |
| >= 0.25 | SIGNIFICANT |

Esses limites são heurísticos e não constituem
prova de degradação do modelo.

## 5. Qualidade da amostra

O detector exige, por padrão, pelo menos
100 transações para executar a análise.

Esse mínimo é operacional e não garante,
isoladamente, confiabilidade estatística.

Amostras insuficientes recebem o status:

`INSUFFICIENT_DATA`

## 6. Procedimento diante de drift

Quando houver drift significativo:

1. Verificar se a amostra é representativa.
2. Confirmar se as features seguem o mesmo esquema
   e pré-processamento utilizados no treinamento.
3. Investigar alterações na origem dos dados.
4. Verificar se o drift persiste em análises posteriores.
5. Avaliar desempenho com dados rotulados,
   quando estiverem disponíveis.
6. Considerar o treinamento de um novo candidato
   caso exista evidência de degradação relevante.

## 7. Avaliação do modelo candidato

Um novo modelo deve ser avaliado utilizando
o pipeline de treinamento e avaliação existente.

As métricas devem considerar o desbalanceamento
do problema de detecção de fraudes, incluindo:

- Precision
- Recall
- F1-score
- PR-AUC
- Matriz de confusão

O candidato deve ser comparado com o modelo
champion atual em um conjunto de avaliação
adequado, sem vazamento de dados.

## 8. Promoção e rollback

A promoção de um novo modelo não é automática.

Após aprovação, o candidato poderá substituir
o champion por meio do processo de registro
e promoção já existente no MLflow.

A versão anterior deverá permanecer disponível
para permitir rollback em caso de problemas.

## 9. Limitações atuais

- O sistema ainda utiliza transações simuladas
  para validar parte do fluxo de monitoramento.
- O PSI não mede diretamente a precisão do modelo.
- A disponibilidade de rótulos reais é necessária
  para confirmar degradação preditiva.
- O monitoramento não executa retreinamento
  ou promoção automática.
- O baseline deve corresponder à versão do modelo
  e ao pré-processamento utilizados em produção.

## 10. Estratégia adotada

O FraudShield AI adota monitoramento contínuo
com investigação e atualização supervisionadas.

O objetivo é preservar a confiabilidade
do modelo sem realizar mudanças automáticas
baseadas exclusivamente em Data Drift.
