import simpy
import numpy as np

def get_random_time(distribution_tuple):
    """Função auxiliar para sortear um tempo de uma distribuição e garantir que seja positivo."""
    dist, params = distribution_tuple
    return max(0, dist.rvs(*params))

class CentralDeEmergencia:
    """
    Usa PriorityResource para filas com prioridade.
    """
    def __init__(self, env, num_bombeiros):
        self.chatbot_resource = simpy.PriorityResource(env, capacity=1)
        self.bombeiros = simpy.PriorityResource(env, capacity=num_bombeiros)

def chamada(env, nome, central, agente_ia, cenario, distributions, stats_locais):
    """
    Processo que simula a jornada de uma chamada.
    """
    tempo_chegada = env.now
    
    # Etapa 1: Classificação e Triagem pelo Agente de IA
    resultado_agente = agente_ia.classify_call(cenario['texto'])
    prioridade = 3 - resultado_agente['info_extraida'].get('original_priority', 2)
    
    print(f"{env.now:.2f}: {nome} (Prioridade {prioridade}) chega.")

    # Etapa 2: Atendimento Inicial (Chatbot ou Humano)
    # Modelamos o tempo de atendimento inicial, que não depende de um recurso com fila
    if resultado_agente['decisao_final'] == 'Complexo':
        stats_locais['chamadas_complexas'] += 1
        print(f"{env.now:.2f}: {nome} (Complexo) sendo atendido por humano.")
        # Tempo de atendimento do operador para casos complexos
        yield env.timeout(get_random_time(distributions['atendimento_operador']))
    else:
        stats_locais['chamadas_simples'] += 1
        print(f"{env.now:.2f}: {nome} (Simples) sendo atendido por chatbot.")
        # Tempo de atendimento 50% mais rápido para o chatbot
        tempo_atendimento_chatbot = get_random_time(distributions['atendimento_operador']) * 0.5
        yield env.timeout(tempo_atendimento_chatbot)
        
    print(f"{env.now:.2f}: {nome} informações coletadas. Entra na fila para bombeiros.")

    # Etapa 3: Fila e Serviço dos Bombeiros
    tempo_entrada_fila_bombeiros = env.now
    with central.bombeiros.request(priority=prioridade) as req_bombeiros:
        yield req_bombeiros
        stats_locais['tempos_espera_bombeiros'].append(env.now - tempo_entrada_fila_bombeiros)
        
        print(f"{env.now:.2f}: {nome} é atendido pelos bombeiros.")
        
        # O tempo de serviço que OCUPA a unidade é apenas o tempo no local
        tempo_servico = get_random_time(distributions['servico_bombeiros'])
        stats_locais['tempos_servico_bombeiros'].append(tempo_servico)
        yield env.timeout(tempo_servico)
        
    stats_locais['tempos_atendimento_total'].append(env.now - tempo_chegada)
    stats_locais['total_chamadas'] += 1
    print(f"{env.now:.2f}: {nome} finaliza o atendimento.")

def gerador_de_chamadas(env, central, agente_ia, cenarios, distributions, stats_locais):
    """
    Gera novas chamadas em intervalos de tempo aleatórios.
    """
    for i, cenario_texto in enumerate(cenarios):
        yield env.timeout(get_random_time(distributions['chegadas']))
        
        cenario_completo = {"texto": cenario_texto, "id": i+1}
        
        env.process(chamada(env, f'Chamada-{i+1}', central, agente_ia, cenario_completo, distributions, stats_locais))

def run_simulation(num_bombeiros, agente_ia, cenarios, distributions):
    """
    Configura e executa um cenário completo de simulação.
    """
    stats_locais = {
        'total_chamadas': 0, 'chamadas_simples': 0, 'chamadas_complexas': 0,
        'tempos_espera_chatbot': [], 'tempos_espera_bombeiros': [],
        'tempos_atendimento_total': [], 'tempos_servico_bombeiros': []
    }
    
    env = simpy.Environment()
    central = CentralDeEmergencia(env, num_bombeiros)
    env.process(gerador_de_chamadas(env, central, agente_ia, cenarios, distributions, stats_locais))
    env.run()
    
    return stats_locais