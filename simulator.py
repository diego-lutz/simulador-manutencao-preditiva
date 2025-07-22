import pandas as pd
from config import *
from machine import Maquina

class PerformanceMonitor:
    """
    Uma classe simples para rastrear as estatísticas de desempenho do modelo de ML em tempo real.
    """
    def __init__(self):
        self.total_predictions = 0; self.correct_predictions = 0; self.false_alarms = 0; self.missed_risks = 0
    def reset(self):
        self.__init__()
    def update(self, true_phase, predicted_phase):
        if predicted_phase == -1: return
        self.total_predictions += 1
        if true_phase == predicted_phase: self.correct_predictions += 1
        else:
            if predicted_phase > true_phase: self.false_alarms += 1
            elif predicted_phase < true_phase: self.missed_risks += 1
    def get_stats(self):
        accuracy = (self.correct_predictions / self.total_predictions) * 100 if self.total_predictions > 0 else 100
        return {"acertos": self.correct_predictions, "erros": self.total_predictions - self.correct_predictions, "alarmes_falsos": self.false_alarms, "riscos_perdidos": self.missed_risks, "acuracia_vivo": f"{accuracy:.2f}%"}

class Simulator:
    """
    Orquestra a simulação completa, gerenciando o parque de máquinas,
    os ciclos de operação, as previsões de ML e os logs.
    """
    def __init__(self, logger, ml_model):
        self.logger = logger
        self.ml_model = ml_model
        self.performance_monitor = PerformanceMonitor()
        self.parque_maquinas = []
        self.contador_maquinas_total = 0
        self.ciclo_atual = 0
        self.total_falhas = 0
        self.is_running = False
        self.historico_sensores = pd.DataFrame()

    def _criar_nova_maquina(self):
        self.contador_maquinas_total += 1
        machine_id = f"PH-{self.contador_maquinas_total:03d}"
        return Maquina(machine_id=machine_id, modelo="Prensa Hidráulica PH-300T")

    def inicializar_parque(self):
        """Preenche o parque de máquinas com um conjunto inicial de máquinas."""
        self.parque_maquinas = [self._criar_nova_maquina() for _ in range(TAMANHO_DO_PARQUE)]
        print(f"Simulator: Parque de {len(self.parque_maquinas)} máquinas inicializado.")
        self.logger.log_event("SIMULATOR", "START", f"Parque de {len(self.parque_maquinas)} máquinas criado.")

    def _executar_previsao_ml(self, maquina: Maquina):
        if self.historico_sensores.empty or 'machine_id' not in self.historico_sensores.columns:
            return
        
        hist_maquina = self.historico_sensores[self.historico_sensores['machine_id'] == maquina.id].tail(24)
        
        if len(hist_maquina) < 24:
            return

        features_dict = {}
        last_row = hist_maquina.iloc[-1]
        features_dict.update(last_row.to_dict())

        windows = [6, 12, 24]
        for window in windows:
            subset = hist_maquina.tail(window)
            features_dict[f'temp_oleo_mean_{window}h'] = subset['temp_oleo'].mean()
            features_dict[f'vibracao_motor_mean_{window}h'] = subset['vibracao_motor'].mean()
            features_dict[f'pressao_hidraulica_mean_{window}h'] = subset['pressao_hidraulica'].mean()
            features_dict[f'temp_oleo_std_{window}h'] = subset['temp_oleo'].std()
            features_dict[f'vibracao_motor_std_{window}h'] = subset['vibracao_motor'].std()
            features_dict[f'pressao_hidraulica_std_{window}h'] = subset['pressao_hidraulica'].std()
            features_dict[f'vibracao_motor_max_{window}h'] = subset['vibracao_motor'].max()

        for k, v in features_dict.items():
            if pd.isna(v): features_dict[k] = 0

        fase_prevista = self.ml_model.predict(features_dict)
        fase_real = maquina.health_phase
        
        self.performance_monitor.update(fase_real, fase_prevista)
        self.logger.log_ml_prediction(maquina.id, fase_real, fase_prevista)

    def executar_ciclo(self):
        self.ciclo_atual += 1
        novos_registros_para_historia = []
        indices_para_substituir = []

        for i, maquina in enumerate(self.parque_maquinas):
            if maquina.health_phase == FASES_SAUDE["Falha"]:
                maquina.tempo_reparo_restante -= HORAS_POR_CICLO
                if maquina.tempo_reparo_restante <= 0:
                    self.logger.archive_machine_history(maquina.id, has_failed=True)
                    indices_para_substituir.append(i)
                continue

            for _ in range(HORAS_POR_CICLO):
                if maquina.health_phase < FASES_SAUDE["Falha"]:
                    maquina.simular_tick()
                    
                    # Salva o dado no arquivo CSV do disco a cada tick (hora)
                    self.logger.log_sensor_tick(maquina)
                    
                    # Coleta o dado para o histórico em memória (para o ML)
                    novos_registros_para_historia.append({
                        'machine_id': maquina.id,
                        'horas_operadas': maquina.horas_operadas,
                        'health_phase': maquina.health_phase,
                        'fator_desgaste': maquina.fator_desgaste,
                        'temp_oleo': maquina.sensores["temp_oleo"].valor_atual,
                        'vibracao_motor': maquina.sensores["vibracao_motor"].valor_atual,
                        'pressao_hidraulica': maquina.sensores["pressao_hidraulica"].valor_atual,
                        'volatilidade_temp': maquina.sensores["temp_oleo"].volatilidade,
                        'volatilidade_vibracao': maquina.sensores["vibracao_motor"].volatilidade,
                        'volatilidade_pressao': maquina.sensores["pressao_hidraulica"].volatilidade
                    })
            
            if maquina.health_phase == FASES_SAUDE["Falha"] and maquina.problema_ativo:
                self.total_falhas += 1
                problema_info = CATALOGO_PROBLEMAS[maquina.problema_ativo]
                self.logger.log_event(maquina.id, "FAILURE", f"Causa: {problema_info['nome_problema']}")
                self.logger.log_event(maquina.id, "REPAIR_STARTED", f"Reparo iniciado. Tempo: {maquina.tempo_reparo_restante}h")
                maquina.problema_ativo = None
    
        if novos_registros_para_historia:
            self.historico_sensores = pd.concat([self.historico_sensores, pd.DataFrame(novos_registros_para_historia)], ignore_index=True)
            max_history_size = TAMANHO_DO_PARQUE * 48 
            if len(self.historico_sensores) > max_history_size:
                self.historico_sensores = self.historico_sensores.tail(max_history_size)

        for maquina in self.parque_maquinas:
            if maquina.health_phase < FASES_SAUDE["Falha"]:
                self._executar_previsao_ml(maquina)

        for i in indices_para_substituir:
            self.parque_maquinas[i] = self._criar_nova_maquina()
            self.logger.log_event(self.parque_maquinas[i].id, "CREATED", f"Nova máquina {self.parque_maquinas[i].id} substituiu a anterior.")

    def run_simulation_loop(self, total_cycles):
        self.is_running = True; self.ciclo_atual = 0; self.total_falhas = 0
        self.performance_monitor.reset(); self.inicializar_parque()
        self.historico_sensores = pd.DataFrame()
        is_infinite = (total_cycles == 0)
        while self.is_running:
            if not is_infinite and self.ciclo_atual >= total_cycles: self.is_running = False; break
            self.executar_ciclo()