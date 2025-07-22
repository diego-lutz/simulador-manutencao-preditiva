import random
from config import *

class Sensor:
    def __init__(self, sensor_id, nome, unidade, faixa_normal):
        self.sensor_id = sensor_id
        self.nome = nome
        self.unidade = unidade
        self.faixa_normal = faixa_normal
        self.volatilidade = 1.0
        self.valor_atual = random.uniform(self.faixa_normal[0], self.faixa_normal[1])

class Maquina:
    def __init__(self, machine_id, modelo):
        self.id = machine_id
        self.modelo = modelo
        self.config = CATALOGO_MAQUINAS[modelo]

        if random.random() < 0.3:
            self.fator_desgaste = random.uniform(FATOR_DESGASTE_INICIAL_MIN_NOVA, FATOR_DESGASTE_INICIAL_MAX_NOVA)
        else:
            self.fator_desgaste = random.uniform(FATOR_DESGASTE_INICIAL_MIN_USADA, FATOR_DESGASTE_INICIAL_MAX_USADA)

        self.sensores = {
            s_cfg["sensor_id"]: Sensor(**s_cfg) for s_cfg in self.config["sensores_config"]
        }
        
        self.health_phase = FASES_SAUDE["Normal"]
        self.horas_operadas = 0
        self.ticks_para_proximo_teste = HORAS_ENTRE_TESTES_DE_SAUDE
        
        self.problema_ativo = None
        self.tempo_reparo_restante = 0

    def realizar_teste_de_saude(self):
        chance_de_evento = self.fator_desgaste / CHANCE_DE_EVENTO_DIVISOR
        if random.random() < chance_de_evento:
            sensor_aleatorio_id = random.choice(list(self.sensores.keys()))
            sensor_afetado = self.sensores[sensor_aleatorio_id]
            sensor_afetado.volatilidade *= AUMENTO_VOLATILIDADE_SENSOR

    def atualizar_fase_saude(self):
        if self.health_phase >= FASES_SAUDE["Falha"]:
            return

        if self.fator_desgaste > 850 or any(s.volatilidade > 3 for s in self.sensores.values()):
            self.health_phase = FASES_SAUDE["Risco_Iminente"]
            return

        if self.fator_desgaste > 600 or any(s.volatilidade > 1.5 for s in self.sensores.values()):
            self.health_phase = FASES_SAUDE["Alerta"]
            return

        self.health_phase = FASES_SAUDE["Normal"]

    def simular_tick(self):
        self.horas_operadas += 1
        self.fator_desgaste += AUMENTO_DESGASTE_POR_HORA
        
        for sensor in self.sensores.values():
            ruido = (random.random() - 0.5) * sensor.volatilidade
            centro_faixa = sum(sensor.faixa_normal) / 2
            tendencia_degragacao = (sensor.valor_atual - centro_faixa) * 0.001
            sensor.valor_atual += ruido + tendencia_degragacao

        self.ticks_para_proximo_teste -= 1
        if self.ticks_para_proximo_teste <= 0:
            self.realizar_teste_de_saude()
            self.ticks_para_proximo_teste = HORAS_ENTRE_TESTES_DE_SAUDE
            
        self.atualizar_fase_saude()

        for id_problema in self.config["problemas_possiveis"]:
            problema = CATALOGO_PROBLEMAS[id_problema]
            gatilho = problema["gatilho_falha"]
            
            valor_a_checar = 0
            if gatilho["sensor_id"] == "fator_desgaste":
                valor_a_checar = self.fator_desgaste
            else:
                valor_a_checar = self.sensores[gatilho["sensor_id"]].valor_atual

            if gatilho["condicao"] == ">" and valor_a_checar > gatilho["valor"]:
                self.iniciar_falha(id_problema)
                break
    
    def iniciar_falha(self, id_problema):
        self.health_phase = FASES_SAUDE["Falha"]
        self.problema_ativo = id_problema
        solucao = CATALOGO_SOLUCOES[CATALOGO_PROBLEMAS[id_problema]["solucao_otima"]]
        self.tempo_reparo_restante = solucao["tempo_base_reparo_h"]

    def concluir_reparo(self):
        self.fator_desgaste += random.uniform(AUMENTO_DESGASTE_POS_REPARO_MIN, AUMENTO_DESGASTE_POS_REPARO_MAX)
        
        for sensor in self.sensores.values():
            sensor.volatilidade = 1.0
            sensor.valor_atual = random.uniform(sensor.faixa_normal[0], sensor.faixa_normal[1])
            
        self.health_phase = FASES_SAUDE["Normal"]
        self.problema_ativo = None
        self.tempo_reparo_restante = 0