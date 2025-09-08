# main.py
import pandas as pd
import numpy as np
import os

# Importa as configurações e os módulos do projeto
import config
from src.analysis.distribution_fitter import find_best_distribution
from src.agent.call_generator import generate_call_scenarios
from src.agent.chatbot import EmergencyResponseAgent
from src.simulation.environment import run_simulation
from src.utils import plotter

def main():
    """
    Função principal que orquestra todo o processo de simulação e análise.
    """
    print("--- INICIANDO PROJETO DE SIMULAÇÃO DE ATENDIMENTO DE EMERGÊNCIA ---")
    
    # 1. Carregar e preparar os dados para análise
    print("\n[ETAPA 1/5] Carregando e preparando dados para análise...")
    try:
        df = pd.read_csv(config.DATASET_PATH, engine='python')
        
        timestamp_cols = ['Received DtTm', 'Entry DtTm', 'On Scene DtTm', 'Available DtTm']
        for col in timestamp_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        df.dropna(subset=timestamp_cols, inplace=True)
        
    except FileNotFoundError:
        print(f"ERRO: Dataset não encontrado em '{config.DATASET_PATH}'. Verifique o caminho.")
        return

    # 2. Encontrar as melhores distribuições de probabilidade
    print("\n[ETAPA 2/5] Analisando distribuições de probabilidade dos tempos...")
    
    df.sort_values('Received DtTm', inplace=True)
    df['tempo_entre_chegadas'] = df['Received DtTm'].diff().dt.total_seconds() / 60.0
    dist_chegadas = find_best_distribution(df[df['tempo_entre_chegadas'] > 0]['tempo_entre_chegadas'].rename("Tempo entre Chegadas"))
    
    df['on_scene_time'] = (df['Available DtTm'] - df['On Scene DtTm']).dt.total_seconds() / 60.0
    dist_servico_bombeiros = find_best_distribution(df[df['on_scene_time'] > 0]['on_scene_time'].rename("Tempo de Serviço no Local"))
    
    df['operator_duration'] = (df['Entry DtTm'] - df['Received DtTm']).dt.total_seconds() / 60.0
    dist_atendimento_operador = find_best_distribution(df[df['operator_duration'] > 0]['operator_duration'].rename("Duração Atendimento Operador"))
    
    # 3. Gerar cenários e instanciar o agente de IA
    print("\n[ETAPA 3/5] Gerando cenários e inicializando o agente de IA...")
    cenarios = generate_call_scenarios(df, config.NUM_CHAMADAS_SIMULADAS)
    agente_ia = EmergencyResponseAgent()

    # 4. Executar a simulação para cada cenário
    print("\n[ETAPA 4/5] Executando os cenários de simulação...")
    all_results = {}
    df_plot_data = pd.DataFrame()
    
    dists = {
        "chegadas": dist_chegadas,
        "atendimento_operador": dist_atendimento_operador,
        "servico_bombeiros": dist_servico_bombeiros,
    }
    
    for n_unidades in config.CENARIOS_UNIDADES:
        print(f"\n--- Cenário com {n_unidades} unidades ---")
        resultados_cenario = run_simulation(
            num_unidades=n_unidades,
            agente_ia=agente_ia,
            cenarios=cenarios,
            distributions=dists
        )
        all_results[n_unidades] = resultados_cenario
        
        temp_df = pd.DataFrame({
            'Tempo de Espera': resultados_cenario.get('tempos_espera_bombeiros', []),
            'Unidades': str(n_unidades)
        })
        df_plot_data = pd.concat([df_plot_data, temp_df], ignore_index=True)
        
    # 5. Apresentar os resultados
    print("\n[ETAPA 5/5] Gerando tabela de resultados e gráficos...")
    
    tabela_resumo = []
    for n_unidades, data in all_results.items():
        tabela_resumo.append({
            'Unidades': n_unidades,
            'Chamadas Atendidas': data.get('total_chamadas', 0),
            'Simples (Chatbot)': data.get('chamadas_simples', 0),
            'Complexas (Humano)': data.get('chamadas_complexas', 0),
            'Tempo médio de espera (min)': np.mean(data.get('tempos_espera_bombeiros', [0])),
            'Tempo médio de serviço (min)': np.mean(data.get('tempos_servico_bombeiros', [0]))
        })
    df_resumo = pd.DataFrame(tabela_resumo)
    print("\n--- Tabela de Resumo dos Resultados (com Chatbot) ---")
    print(df_resumo.to_string(index=False))

    path_tabela = os.path.join(config.RESULTS_DIR, "tables", "resumo_simulacao.csv")
    df_resumo.to_csv(path_tabela, index=False)
    print(f"\n-> Tabela salva em: {path_tabela}")
    
    plotter.plot_boxplot(df_plot_data)
    plotter.plot_distribution(df_plot_data)
    plotter.plot_cumulative_wait_time(all_results)
    
    print("\n--- PROJETO FINALIZADO ---")

if __name__ == "__main__":
    main()