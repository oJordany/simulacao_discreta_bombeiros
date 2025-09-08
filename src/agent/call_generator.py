import pandas as pd
import random
import json
import os
import config

# banco de dados JSON
JSON_BANK_PATH = os.path.join(config.BASE_DIR, "src", "agent", "data", "natural_language_bank.json")

def load_natural_language_bank():
    """
    Carrega o banco de dados de frases a partir do arquivo JSON.
    """
    try:
        with open(JSON_BANK_PATH, 'r', encoding='utf-8') as f:
            bank = json.load(f)
        return bank
    except FileNotFoundError:
        print(f"ERRO: Banco de dados de frases não encontrado em '{JSON_BANK_PATH}'")
        print("Certifique-se de que o arquivo existe na pasta src/agent/data/")
        return None
    except json.JSONDecodeError:
        print(f"ERRO: O arquivo '{JSON_BANK_PATH}' não é um JSON válido.")
        return None

def generate_call_scenarios(df, num_calls):
    """
    Gera uma lista de textos de chamada em linguagem natural baseada na
    distribuição de probabilidade dos Call Types do dataset.
    """
    print(f"\nGerando {num_calls} cenários de chamada...")
    
    natural_language_bank = load_natural_language_bank()
    if not natural_language_bank:
        # Se não conseguir carregar o banco, interrompe a geração
        return []

    # Calcula a frequência de cada Call Type
    call_type_weights = df['Call Type'].value_counts(normalize=True)
    
    # Sorteia os Call Types com base na sua frequência real
    call_type_list = call_type_weights.index.tolist()
    weights_list = call_type_weights.values.tolist()
    
    generated_call_types = random.choices(call_type_list, weights=weights_list, k=num_calls)
    
    # Para cada Call Type sorteado, escolhe uma frase aleatória do banco
    call_scenarios = []
    for call_type in generated_call_types:
        # Se o tipo de chamada sorteado não estiver no nosso banco,
        # usamos um tipo genérico como 'Medical Incident' para não quebrar a simulação.
        phrases = natural_language_bank.get(call_type, natural_language_bank.get("Medical Incident", ["Chamada de emergência genérica."]))
        call_scenarios.append(random.choice(phrases))
        
    print("-> Cenários gerados com sucesso.")
    return call_scenarios