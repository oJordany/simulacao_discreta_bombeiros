import pandas as pd
import numpy as np
import simpy
import matplotlib.pyplot as plt
import seaborn as sns
from config import config

def emergency_call(env, call_id, service_time, units, metrics):
    arrival = env.now
    with units.request() as req:
        yield req
        wait = env.now - arrival
        metrics["wait_times"].append(wait)
        yield env.timeout(service_time)
        metrics["service_times"].append(service_time)
        metrics["served"] += 1


def call_generator(env, df, units, metrics):
    for _, row in df.iterrows():
        yield env.timeout(row["Interarrival"])
        env.process(emergency_call(env, row["Incident Number"], row["Service Time"], units, metrics))


def run_simulation(num_units, df):
    env = simpy.Environment()
    units = simpy.Resource(env, capacity=num_units)
    metrics = {"wait_times": [], "service_times": [], "served": 0}
    env.process(call_generator(env, df, units, metrics))
    env.run()

    results = {
        "num_units": num_units,
        "served": metrics["served"],
        "avg_wait": np.mean(metrics["wait_times"]) if metrics["wait_times"] else 0,
        "avg_service": np.mean(metrics["service_times"]) if metrics["service_times"] else 0
    }
    return results, metrics

df_clean = pd.read_csv(config.DATASET_PATH, engine='python')

df_clean['Received DtTm'] = pd.to_datetime(df_clean['Received DtTm'])
df_clean['Response DtTm'] = pd.to_datetime(df_clean['Response DtTm'])
df_clean['Available DtTm'] = pd.to_datetime(df_clean['Available DtTm'])

df_clean['Service Time'] = (df_clean['Available DtTm'] - df_clean['Response DtTm']).dt.total_seconds() / 60
df_clean['Service Time'] = df_clean['Service Time'].clip(lower=0)

df_clean['Interarrival'] = df_clean['Received DtTm'].diff().dt.total_seconds().div(60).fillna(0).clip(lower=0)


df_clean['Service Time'] = (df_clean['Available DtTm'] - df_clean['Response DtTm']).dt.total_seconds() / 60
df_clean['Interarrival'] = df_clean['Received DtTm'].diff().dt.total_seconds() / 60


print("Total de chamadas na base de dados:", len(df_clean))

df_sim = df_clean.head(5000)

print("Total de chamadas usadas na simulação:", len(df_sim))

cenarios = [3, 5, 8, 10]
resultados = []
metricas = {}

for c in cenarios:
    res, met = run_simulation(c, df_sim)
    resultados.append(res)
    metricas[c] = met

sns.set_theme(style="whitegrid")

# a) Boxplot comparativo do tempo de espera
plt.figure(figsize=(10,6))
sns.boxplot(data=[metricas[c]["wait_times"] for c in cenarios], palette="Set2")
plt.xticks(range(len(cenarios)), [f"{c} unidades" for c in cenarios])
plt.ylabel("Tempo de espera (min)")
plt.title("Comparação de Tempo de Espera entre Cenários")
plt.show()

# b) Histograma dos tempos de espera
plt.figure(figsize=(10,6))
for c in cenarios:
    sns.histplot(metricas[c]["wait_times"], label=f"{c} unidades", kde=True, bins=30, stat="density")
plt.xlabel("Tempo de espera (min)")
plt.ylabel("Densidade")
plt.title("Distribuição do Tempo de Espera")
plt.legend()
plt.show()

# c) Linha do tempo acumulada de chamadas atendidas
plt.figure(figsize=(10,6))
for c in cenarios:
    plt.plot(np.cumsum([1]*len(metricas[c]["wait_times"])), sorted(metricas[c]["wait_times"]), label=f"{c} unidades")
plt.xlabel("Número de chamadas")
plt.ylabel("Tempo de espera (min)")
plt.title("Tempo de Espera por Chamada (Acumulado)")
plt.legend()
plt.show()

# d) Tabela resumida
df_results = pd.DataFrame(resultados)
print("\n=== Resumo dos Cenários ===")
print(df_results)
