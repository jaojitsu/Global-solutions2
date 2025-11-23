"""
Funções utilitárias para calcular métricas simples de fairness em dados simulados.
"""

import pandas as pd

def disparate_impact(df: pd.DataFrame, group_col: str, outcome_col: str):
    """
    df: DataFrame com colunas group_col (ex: 'grupo') e outcome_col (ex: aprovado 0/1)
    Retorna razão de aprovação grupo_min / grupo_max.
    """
    rates = df.groupby(group_col)[outcome_col].mean()
    if rates.empty or len(rates) < 2:
        return None
    min_rate = rates.min()
    max_rate = rates.max()
    if max_rate == 0:
        return None
    return float(min_rate / max_rate)

if __name__ == "__main__":
    disparate_impact()
