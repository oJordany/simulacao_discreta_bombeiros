import pandas as pd
import numpy as np
import scipy.stats as st
import warnings

warnings.filterwarnings('ignore')

def find_best_distribution(data_series):
    """
    Testa várias distribuições de probabilidade em uma série de dados e retorna a melhor
    com base no teste de Kolmogorov-Smirnov (KS).
    """
    print(f"Iniciando busca pela melhor distribuição para '{data_series.name}'...")
    
    # Lista de distribuições a serem testadas que SÃO SEMPRE NÃO-NEGATIVAS.
    distributions = [
        st.expon,       # Exponencial: Clássica para tempos de chegada
        st.lognorm,     # Log-Normal: Comum para tempos de serviço
        st.gamma,       # Gamma: Flexível para tempos de espera
        st.weibull_min  # Weibull: Usada em análises de confiabilidade e tempo de vida
    ]
    
    best_distribution = None
    best_params = None
    best_ks_stat = np.inf

    for distribution in distributions:
        try:
            params = distribution.fit(data_series)
            D, p_value = st.kstest(data_series, distribution.name, args=params)
            
            if D < best_ks_stat:
                best_ks_stat = D
                best_distribution = distribution
                best_params = params
        except Exception:
            continue

    print(f"-> Melhor distribuição encontrada: {best_distribution.name}")
    print(f"-> Parâmetros: {best_params}")
    return best_distribution, best_params