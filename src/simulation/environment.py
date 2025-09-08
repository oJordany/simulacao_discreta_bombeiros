# src/simulation/environment.py
import simpy
import numpy as np

def get_random_time(distribution_tuple):
    """Função auxiliar para sortear um tempo de uma distribuição e garantir que seja positivo."""
    dist, params = distribution_tuple
    return max(0, dist.rvs(*params))

class CentralDeEmergencia:
    """
    O único recurso com fila são as unidades de bombeiros.
    """
    def __init__(self, env, num_unidades):
        self.bombeiros = simpy.PriorityResource(env, capacity=num_unidades)

def chamada(env, nome, central, agente_ia, cenario, distributions, stats_locais):
    """
    Processo que simula a jornada completa de uma chamada.
    """
    stats_locais['total_chamadas'] += 1
    tempo_chegada = env.now
    
    # Etapa 1: Triagem imediata pelo Agente de IA, que usa o modelo de ML internamente.
    resultado_agente = agente_ia.classify_call(cenario['texto'])
    prioridade = 3 - resultado_agente['info_extraida'].get('original_priority', 2)
    
    print(f"{env.now:.2f}: {nome} (Prioridade {prioridade}) chega.")


    decisao_modelo = resultado_agente['decisao_final']
    
    if decisao_modelo == 'Simples':
        stats_locais['chamadas_simples'] += 1
        print(f"{env.now:.2f}: {nome} (Classificado como Simples) sendo atendido por chatbot...")
        
        # Simula o tempo de atendimento do chatbot para coletar informações.
        tempo_atendimento = get_random_time(distributions['atendimento_simples']) * 0.5
        yield env.timeout(tempo_atendimento)
        
        print(f"{env.now:.2f}: {nome} (Simples) entra na fila para despacho.")
        
    else: # Se a decisão do modelo for 'Complexo'
        stats_locais['chamadas_complexas'] += 1
        print(f"{env.now:.2f}: {nome} (Classificado como Complexo) sendo atendido por humano...")
        
        # Simula o tempo de atendimento de um operador humano.
        yield env.timeout(get_random_time(distributions['atendimento_humano']))
        
        print(f"{env.now:.2f}: {nome} (Complexo) entra na fila para despacho.")

    # --- ETAPA COMUM: Fila e Serviço dos Bombeiros ---
    # Todas as chamadas, simples ou complexas, que precisam de uma unidade, chegam aqui.
    
    tempo_entrada_fila_bombeiros = env.now
    with central.bombeiros.request(priority=prioridade) as req_bombeiros:
        yield req_bombeiros
        stats_locais['tempos_espera_bombeiros'].append(env.now - tempo_entrada_fila_bombeiros)
        
        print(f"{env.now:.2f}: {nome} é atendido pelos bombeiros.")
        
        tempo_servico = get_random_time(distributions['servico_bombeiros'])
        stats_locais['tempos_servico_bombeiros'].append(tempo_servico)
        yield env.timeout(tempo_servico)
        
    stats_locais['tempos_atendimento_total'].append(env.now - tempo_chegada)
    print(f"{env.now:.2f}: {nome} finaliza o atendimento.")

def gerador_de_chamadas(env, central, agente_ia, cenarios, distributions, stats_locais):
    """
    Gera novas chamadas em intervalos de tempo aleatórios.
    """
    for i, cenario_texto in enumerate(cenarios):
        yield env.timeout(get_random_time(distributions['chegadas']))
        cenario_completo = {"texto": cenario_texto, "id": i+1}
        env.process(chamada(env, f'Chamada-{i+1}', central, agente_ia, cenario_completo, distributions, stats_locais))

def run_simulation(num_unidades, agente_ia, cenarios, distributions):
    """
    Configura e executa um cenário completo de simulação.
    """
    stats_locais = {
        'total_chamadas': 0, 
        'chamadas_simples': 0, 
        'chamadas_complexas': 0,
        'tempos_espera_bombeiros': [],
        'tempos_atendimento_total': [],
        'tempos_servico_bombeiros': []
    }
    
    env = simpy.Environment()
    central = CentralDeEmergencia(env, num_unidades)
    env.process(gerador_de_chamadas(env, central, agente_ia, cenarios, distributions, stats_locais))
    env.run()
    
    return stats_locais