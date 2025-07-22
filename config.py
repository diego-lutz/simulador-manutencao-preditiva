import random

# --- PARÂMETROS DA SIMULAÇÃO ---
TAMANHO_DO_PARQUE = 10
HORAS_POR_CICLO = 24
HORAS_ENTRE_TESTES_DE_SAUDE = 8

# --- PARÂMETROS DE DEGRADAÇÃO DA MÁQUINA ---
FATOR_DESGASTE_INICIAL_MIN_NOVA = 50.0
FATOR_DESGASTE_INICIAL_MAX_NOVA = 250.0
FATOR_DESGASTE_INICIAL_MIN_USADA = 500.0
FATOR_DESGASTE_INICIAL_MAX_USADA = 700.0
AUMENTO_DESGASTE_POR_HORA = 0.05
AUMENTO_DESGASTE_POS_REPARO_MIN = 75.0
AUMENTO_DESGASTE_POS_REPARO_MAX = 200.0

# --- PARÂMETROS DE EVENTOS PROBABILÍSTICOS ---
CHANCE_DE_EVENTO_DIVISOR = 25000.0
AUMENTO_VOLATILIDADE_SENSOR = 1.5

# --- DEFINIÇÃO DAS FASES DE SAÚDE ---
FASES_SAUDE = {
    "Normal": 0,
    "Alerta": 1,
    "Risco_Iminente": 2,
    "Falha": 3
}

# --- CATÁLOGO DE SOLUÇÕES DE MANUTENÇÃO ---
CATALOGO_SOLUCOES = {
    "SOL-H02": {"procedimento": "Limpar Trocador de Calor", "tempo_base_reparo_h": 24},
    "SOL-M01": {"procedimento": "Alinhamento a Laser de Eixo", "tempo_base_reparo_h": 8},
    "SOL-G01": {"procedimento": "Revisão Geral e Substituição de Componentes", "tempo_base_reparo_h": 48}
}

# --- CATÁLOGO DE PROBLEMAS E GATILHOS DE FALHA ---
CATALOGO_PROBLEMAS = {
    "PROB-PH-001": {
        "nome_problema": "Superaquecimento Crítico do Óleo",
        "gatilho_falha": {"sensor_id": "temp_oleo", "condicao": ">", "valor": 95.0},
        "solucao_otima": "SOL-H02"
    },
    "PROB-PH-002": {
        "nome_problema": "Vibração Destrutiva do Motor",
        "gatilho_falha": {"sensor_id": "vibracao_motor", "condicao": ">", "valor": 7.5},
        "solucao_otima": "SOL-M01"
    },
    "PROB-PH-003": {
        "nome_problema": "Falha Geral por Desgaste",
        "gatilho_falha": {"sensor_id": "fator_desgaste", "condicao": ">", "valor": 1000.0},
        "solucao_otima": "SOL-G01"
    }
}

# --- CATÁLOGO DE MODELOS DE MÁQUINAS ---
CATALOGO_MAQUINAS = {
    "Prensa Hidráulica PH-300T": {
        "nome_amigavel": "Prensa Hidráulica 300 Ton",
        "sensores_config": [
            {"sensor_id": "temp_oleo", "nome": "Temperatura do Óleo", "unidade": "°C", "faixa_normal": (45.0, 65.0)},
            {"sensor_id": "vibracao_motor", "nome": "Vibração do Motor Principal", "unidade": "mm/s", "faixa_normal": (0.5, 2.0)},
            {"sensor_id": "pressao_hidraulica", "nome": "Pressão Fluido Hidráulico", "unidade": "bar", "faixa_normal": (180.0, 220.0)}
        ],
        "problemas_possiveis": [
            "PROB-PH-001",
            "PROB-PH-002",
            "PROB-PH-003"
        ]
    }
}