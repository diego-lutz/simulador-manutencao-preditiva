import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import time

from config import *
from machine import Maquina

def generate_training_data(num_machines, hours_per_machine):
    total_hours = num_machines * hours_per_machine
    print(f"Gerando dados de treinamento de {num_machines} máquinas ({total_hours} horas totais)...")
    
    all_records = []
    start_time = time.time()

    for i in range(num_machines):
        if i % 10 == 0 and i > 0:
            print(f"  ...simulando máquina {i}/{num_machines}")
        
        machine = Maquina(machine_id=f"TRAIN-{i:03d}", modelo="Prensa Hidráulica PH-300T")
        
        for _ in range(hours_per_machine):
            if machine.health_phase == FASES_SAUDE["Falha"]:
                machine.concluir_reparo()

            machine.simular_tick()
            
            record = {
                'machine_id': machine.id,
                'horas_operadas': machine.horas_operadas,
                'health_phase': machine.health_phase,
                'fator_desgaste': machine.fator_desgaste,
                'temp_oleo': machine.sensores["temp_oleo"].valor_atual,
                'vibracao_motor': machine.sensores["vibracao_motor"].valor_atual,
                'pressao_hidraulica': machine.sensores["pressao_hidraulica"].valor_atual,
                'volatilidade_temp': machine.sensores["temp_oleo"].volatilidade,
                'volatilidade_vibracao': machine.sensores["vibracao_motor"].volatilidade,
                'volatilidade_pressao': machine.sensores["pressao_hidraulica"].volatilidade
            }
            all_records.append(record)
            
    print(f"Geração de dados brutos concluída em {time.time() - start_time:.2f} segundos.")
    return pd.DataFrame(all_records)

def engineer_features(df):
    print("Iniciando engenharia de features de série temporal...")
    start_time = time.time()
    
    df = df.sort_values(by=['machine_id', 'horas_operadas']).reset_index(drop=True)
    grouped = df.groupby('machine_id')
    windows = [6, 12, 24]
    
    for window in windows:
        rolling_features = grouped.rolling(window=window, min_periods=1).agg({
            'temp_oleo': ['mean', 'std'],
            'vibracao_motor': ['mean', 'std', 'max'],
            'pressao_hidraulica': ['mean', 'std']
        })
        rolling_features.columns = [f'{col[0]}_{col[1]}_{window}h' for col in rolling_features.columns]
        df = pd.concat([df, rolling_features.reset_index(drop=True)], axis=1)

    df.dropna(inplace=True)
    print(f"Engenharia de features concluída em {time.time() - start_time:.2f} segundos.")
    return df

def train_and_save_model(df):
    print("\nIniciando treinamento do modelo...")
    df_train = df[df['health_phase'] != FASES_SAUDE["Falha"]].copy()

    print("Distribuição das classes nos dados de treinamento:")
    print(df_train['health_phase'].value_counts())

    features = [col for col in df_train.columns if col not in ['machine_id', 'health_phase']]
    target = 'health_phase'
    
    X = df_train[features]
    y = df_train[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced', n_jobs=-1, max_depth=20, min_samples_leaf=5)
    
    print("Treinando o RandomForest Classifier com features avançadas...")
    start_time = time.time()
    model.fit(X_train, y_train)
    print(f"Treinamento concluído em {time.time() - start_time:.2f} segundos.")
    
    print("\n--- AVALIAÇÃO DO MODELO ---")
    y_pred = model.predict(X_test)
    
    class_labels = sorted([num for name, num in FASES_SAUDE.items() if num != FASES_SAUDE["Falha"]])
    class_names = [name for name, num in sorted(FASES_SAUDE.items()) if num in class_labels]

    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred, labels=class_labels, target_names=class_names, zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred, labels=class_labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Matriz de Confusão do Modelo Treinado')
    plt.ylabel('Fase Real')
    plt.xlabel('Fase Prevista')
    plt.show()

    model_filename = "predictive_model.joblib"
    print(f"\nSalvando o modelo em '{model_filename}'...")
    joblib.dump(model, model_filename)
    print("Modelo salvo com sucesso!")

if __name__ == "__main__":
    NUM_MAQUINAS_TREINO = 50
    HORAS_POR_MAQUINA = 5000 
    
    df_raw = generate_training_data(NUM_MAQUINAS_TREINO, HORAS_POR_MAQUINA)
    df_featured = engineer_features(df_raw)
    train_and_save_model(df_featured)