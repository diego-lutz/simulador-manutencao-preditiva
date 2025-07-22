import os
import joblib
import pandas as pd

class MLModel:
    def __init__(self, model_path="predictive_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.features = [
            'horas_operadas',
            'fator_desgaste', 'temp_oleo', 'vibracao_motor', 'pressao_hidraulica',
            'volatilidade_temp', 'volatilidade_vibracao', 'volatilidade_pressao',
            'temp_oleo_mean_6h', 'temp_oleo_std_6h', 'vibracao_motor_mean_6h',
            'vibracao_motor_std_6h', 'vibracao_motor_max_6h', 'pressao_hidraulica_mean_6h',
            'pressao_hidraulica_std_6h', 'temp_oleo_mean_12h', 'temp_oleo_std_12h',
            'vibracao_motor_mean_12h', 'vibracao_motor_std_12h', 'vibracao_motor_max_12h',
            'pressao_hidraulica_mean_12h', 'pressao_hidraulica_std_12h',
            'temp_oleo_mean_24h', 'temp_oleo_std_24h', 'vibracao_motor_mean_24h',
            'vibracao_motor_std_24h', 'vibracao_motor_max_24h',
            'pressao_hidraulica_mean_24h', 'pressao_hidraulica_std_24h'
        ]

    def load(self):
        if not os.path.exists(self.model_path):
            print(f"Erro Crítico: Arquivo do modelo '{self.model_path}' não encontrado.")
            print("Por favor, execute o script 'train_model.py' primeiro.")
            return False
        try:
            self.model = joblib.load(self.model_path)
            print(f"Modelo de ML carregado com sucesso de '{self.model_path}'.")
            return True
        except Exception as e:
            print(f"Erro ao carregar o modelo de '{self.model_path}'. Erro: {e}")
            return False

    def predict(self, feature_dict):
        if self.model is None:
            return -1
        try:
            input_df = pd.DataFrame([feature_dict])
            input_df = input_df[self.features]
            prediction = self.model.predict(input_df)
            return prediction[0]
        except Exception as e:
            print(f"Erro durante a previsão do ML. Dados de entrada podem estar incompletos. Erro: {e}")
            return -1