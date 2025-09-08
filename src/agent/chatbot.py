import joblib
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

import config
from . import prompts

import langchain
from langchain.cache import InMemoryCache

class EmergencyCallInfo(BaseModel):
    """Estrutura para armazenar as informações extraídas da chamada."""
    call_type: str = Field(description="O tipo específico do incidente.")
    call_type_group: str = Field(description="A categoria geral do incidente.")
    original_priority: int = Field(description="A urgência inicial da chamada (2 ou 3).")

class EmergencyCallInfo(BaseModel):
    """Estrutura para armazenar as informações extraídas da chamada."""
    call_type: str = Field(description="O tipo específico do incidente.")
    call_type_group: str = Field(description="A categoria geral do incidente.")
    original_priority: int = Field(description="A urgência inicial da chamada (1, 2 ou 3).")

class EmergencyResponseAgent:
    def __init__(self):
        print("Inicializando o Agente de Resposta a Emergências (usando Ollama)...")
        
        # --- CACHE ---
        langchain.llm_cache = InMemoryCache()
        print("Cache em memória para o LLM ativado.")
        
        # 1. Carrega o modelo de ML e o pré-processador
        try:
            self.preprocessor = joblib.load(config.PREPROCESSOR_PATH)
            self.classifier = joblib.load(config.CLASSIFIER_PATH)
            print("Modelos de ML carregados com sucesso.")
        except FileNotFoundError as e:
            print(f"Erro: Arquivo de modelo não encontrado. {e}")
            print(f"Certifique-se de que os arquivos estão na pasta '{config.MODELS_DIR}'.")
            raise
            
        # 2. Configura o LLM para usar o Ollama local
        self.llm = ChatOllama(
            model=config.OLLAMA_MODEL,
            temperature=0.0
        )
        self.extraction_chain = ChatPromptTemplate.from_template(prompts.PROMPT_TEMPLATE) | self.llm.with_structured_output(EmergencyCallInfo)
        print(f"Agente pronto para operar com o modelo local '{config.OLLAMA_MODEL}'.")

    def classify_call(self, natural_language_input: str) -> dict:
        """
        Processa um texto de chamada, extrai as features iniciais e classifica a complexidade.
        """
        print(f"\nProcessando nova chamada: '{natural_language_input}'")
        
        # Etapa 1: Extrair features com o LLM local
        print("-> Etapa 1: Extraindo informações iniciais com o LLM (Ollama, com cache)...")
        extracted_info = self.extraction_chain.invoke({"natural_language_input": natural_language_input})
        
        print("-> Etapa 2: Preparando dados para o classificador de complexidade...")
        input_df = pd.DataFrame([{
            "Call Type": extracted_info.call_type,
            "Call Type Group": extracted_info.call_type_group,
            "Original Priority": extracted_info.original_priority
        }])
        
        processed_input = self.preprocessor.transform(input_df)
        
        print("-> Etapa 3: Classificando a complexidade...")
        prediction = self.classifier.predict(processed_input)
        complexity = "Complexo" if prediction[0] == 1 else "Simples"
        
        result = {
            "texto_original": natural_language_input,
            "info_extraida": extracted_info.dict(),
            "decisao_final": complexity
        }
        
        print(f"--> Decisão Final: {complexity}")
        return result