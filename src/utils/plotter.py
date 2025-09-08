# src/utils/plotter.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import config

# Configura o estilo dos gráficos
plt.style.use('seaborn-v0_8-whitegrid')

def plot_boxplot(df_plot_data, save=True):
    """Gera um boxplot comparativo dos tempos de espera."""
    print("Gerando gráfico: Boxplot Comparativo do Tempo de Espera...")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='Unidades', y='Tempo de Espera', data=df_plot_data, ax=ax)
    ax.set_title('Boxplot Comparativo do Tempo de Espera por Unidade (com Chatbot)', fontsize=16)
    ax.set_xlabel('Número de Unidades de Bombeiros', fontsize=12)
    ax.set_ylabel('Tempo de Espera por Bombeiros (minutos)', fontsize=12)
    
    if save:
        path = os.path.join(config.BASE_DIR, "results", "plots", "boxplot_tempo_espera.png")
        plt.savefig(path)
        print(f"-> Gráfico salvo em: {path}")
    plt.show()

def plot_distribution(df_plot_data, save=True):
    """Gera um gráfico de distribuição dos tempos de espera."""
    print("Gerando gráfico: Distribuição do Tempo de Espera...")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.kdeplot(data=df_plot_data, x='Tempo de Espera', hue='Unidades', 
                fill=True, common_norm=False, alpha=0.3, ax=ax, bw_adjust=.5)
    ax.set_title('Distribuição do Tempo de Espera para Diferentes Números de Unidades', fontsize=16)
    ax.set_xlabel('Tempo de Espera por Bombeiros (minutos)', fontsize=12)
    ax.set_ylabel('Densidade', fontsize=12)
    
    if save:
        path = os.path.join(config.BASE_DIR, "results", "plots", "distribuicao_tempo_espera.png")
        plt.savefig(path)
        print(f"-> Gráfico salvo em: {path}")
    plt.show()

def plot_cumulative_wait_time(all_results, save=True):
    """Gera um gráfico do tempo de espera acumulado."""
    print("Gerando gráfico: Tempo de Espera Acumulado...")
    fig, ax = plt.subplots(figsize=(10, 6))
    for n_unidades, data in all_results.items():
        tempos_de_espera = data.get('tempos_espera_bombeiros', [])
        if tempos_de_espera:
            tempos_acumulados = np.cumsum(np.sort(tempos_de_espera))
            ax.plot(range(len(tempos_acumulados)), tempos_acumulados, label=f'{n_unidades} unidades')

    ax.set_title('Tempo de Espera Acumulado por Chamada (com Chatbot)', fontsize=16)
    ax.set_xlabel('Número de Chamadas Atendidas', fontsize=12)
    ax.set_ylabel('Tempo de Espera Acumulado Total (minutos)', fontsize=12)
    ax.legend()
    
    if save:
        path = os.path.join(config.BASE_DIR, "results", "plots", "acumulado_tempo_espera.png")
        plt.savefig(path)
        print(f"-> Gráfico salvo em: {path}")
    plt.show()