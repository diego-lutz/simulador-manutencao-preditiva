import os
import csv
from datetime import datetime
import pandas as pd

class DataLogger:
    """
    Gerencia todas as operações de I/O (Input/Output) para os logs da simulação.
    Cria diretórios, escreve nos logs ativos e arquiva os históricos das máquinas.
    """
    def __init__(self, base_dir="logs"):
        # --- Definição da Estrutura de Diretórios ---
        self.base_dir = base_dir
        self.active_dir = os.path.join(self.base_dir, "active_simulation")
        self.archive_dir = os.path.join(self.base_dir, "archived_data")
        self.success_dir = os.path.join(self.archive_dir, "successful_runs")
        self.failure_dir = os.path.join(self.archive_dir, "failure_reports")

        # --- Definição dos Arquivos de Log Ativos ---
        self.sensor_log_path = os.path.join(self.active_dir, "sensor_log.csv")
        self.event_log_path = os.path.join(self.active_dir, "event_log.csv")
        self.ml_predictions_log_path = os.path.join(self.active_dir, "ml_predictions_log.csv")

        # --- Definição dos Cabeçalhos dos CSVs ---
        self.SENSOR_HEADER = [
            'timestamp', 'machine_id', 'health_phase', 'fator_desgaste',
            'temp_oleo', 'vibracao_motor', 'pressao_hidraulica',
            'volatilidade_temp', 'volatilidade_vibracao', 'volatilidade_pressao'
        ]
        self.EVENT_HEADER = ['timestamp', 'machine_id', 'event_type', 'description']
        self.ML_PREDICTIONS_HEADER = ['timestamp', 'machine_id', 'true_phase', 'predicted_phase', 'is_correct']

    def setup_directories_and_logs(self):
        """
        Cria toda a estrutura de diretórios e inicializa os arquivos de log
        no início de uma nova execução da simulação.
        """
        for path in [self.active_dir, self.success_dir, self.failure_dir]:
            os.makedirs(path, exist_ok=True)
        
        with open(self.sensor_log_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(self.SENSOR_HEADER)
        with open(self.event_log_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(self.EVENT_HEADER)
        with open(self.ml_predictions_log_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(self.ML_PREDICTIONS_HEADER)
        
        print("Logger: Estrutura de diretórios e logs iniciais criados com sucesso.")

    def log_sensor_tick(self, machine):
        """Registra o estado atual dos sensores e da máquina em uma nova linha do log."""
        with open(self.sensor_log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                machine.id,
                machine.health_phase,
                round(machine.fator_desgaste, 2),
                round(machine.sensores["temp_oleo"].valor_atual, 2),
                round(machine.sensores["vibracao_motor"].valor_atual, 2),
                round(machine.sensores["pressao_hidraulica"].valor_atual, 2),
                round(machine.sensores["temp_oleo"].volatilidade, 2),
                round(machine.sensores["vibracao_motor"].volatilidade, 2),
                round(machine.sensores["pressao_hidraulica"].volatilidade, 2),
            ])

    def log_event(self, machine_id, event_type, description):
        """Registra um evento discreto (ex: início de reparo, falha)."""
        with open(self.event_log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                machine_id,
                event_type,
                description
            ])
            
    def log_ml_prediction(self, machine_id, true_phase, predicted_phase):
        """Registra o resultado de uma previsão do modelo de ML."""
        with open(self.ml_predictions_log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            is_correct = (true_phase == predicted_phase)
            writer.writerow([
                datetime.now().isoformat(),
                machine_id,
                true_phase,
                predicted_phase,
                is_correct
            ])

    def archive_machine_history(self, machine_id, has_failed=True):
        """
        Coleta todo o histórico de uma máquina do log ativo e o salva
        em um arquivo de relatório no diretório de arquivamento apropriado.
        """
        try:
            # Usar pandas para ler e filtrar o CSV é muito eficiente
            df_sensors = pd.read_csv(self.sensor_log_path)
            df_machine_history = df_sensors[df_sensors['machine_id'] == machine_id]

            if df_machine_history.empty:
                print(f"Logger Warning: Nenhum dado encontrado para a máquina {machine_id} no log ativo.")
                return

            destination_dir = self.failure_dir if has_failed else self.success_dir
            report_path = os.path.join(destination_dir, f"report_{machine_id}.csv")
            
            # Salva o histórico da máquina no seu próprio arquivo de relatório
            df_machine_history.to_csv(report_path, index=False)
            
            print(f"Logger: Histórico da máquina {machine_id} arquivado em {report_path}")

        except FileNotFoundError:
            print(f"Logger Error: Arquivo de log ativo não encontrado para arquivamento.")
        except Exception as e:
            print(f"Logger Error: Falha ao arquivar o histórico da máquina {machine_id}. Erro: {e}")