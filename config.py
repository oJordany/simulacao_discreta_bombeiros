import os
from dotenv import load_dotenv

load_dotenv()

# --- Caminhos do Projeto ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "feature_preprocessor_final.pkl")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "best_classifier_pipeline.pkl")
DATASET_PATH = os.path.join(DATA_DIR, "Fire_Department_and_Emergency_Medical_Services_Dispatched_Calls_for_Service_20250904.csv")

# --- Parâmetros da Simulação ---
NUM_CHAMADAS_SIMULADAS = 5000  # Número de chamadas para simular em cada cenário
CENARIOS_UNIDADES = [3, 5, 8, 10] # Cenários de unidades de bombeiros a testar

OLLAMA_MODEL = "phi3"