# Simulador de Manutenção Preditiva com IA

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

### Um Estudo sobre Simulação de Dados e Machine Learning

Este projeto é, acima de tudo, um objeto de estudo e uma experiência de desenvolvimento. O objetivo foi criar um ecossistema completo, do zero, para simular um ambiente industrial, gerar dados de falha realistas e, por fim, treinar um modelo de Machine Learning capaz de realizar manutenção preditiva.

Uma característica fundamental deste projeto é que ele foi **desenvolvido em colaboração com uma Inteligência Artificial (Gemini, do Google)**. O processo envolveu o direcionamento humano na arquitetura, na lógica de negócio e na depuração, enquanto a IA atuou como uma poderosa ferramenta de geração de código, diagnóstico de bugs e refinamento de ideias, demonstrando um novo paradigma de desenvolvimento de software assistido por IA.

---

## 🚀 Conceitos Principais

O projeto é construído sobre três pilares técnicos:

1.  **Simulação Dinâmica e Realista:** O núcleo do projeto é um simulador que gerencia um "parque" de máquinas virtuais. Cada máquina possui um ciclo de vida complexo, com um **Fator de Desgaste** que simula seu envelhecimento e uma **Volatilidade** de sensores que aumenta após "eventos de degradação" probabilísticos. Isso garante que os dados gerados não sejam lineares, mas sim ricos e imprevisíveis, como no mundo real.

2.  **Machine Learning Preditivo:** O sistema utiliza um modelo de `RandomForestClassifier` treinado para analisar os dados dos sensores em tempo real. O objetivo do modelo não é apenas prever a falha, mas classificar a máquina em diferentes **fases de saúde** (`Normal`, `Alerta`, `Risco Iminente`), fornecendo um prognóstico muito mais útil.

3.  **Dashboard Interativo:** Uma interface gráfica construída com `Tkinter` permite ao usuário iniciar, parar e monitorar a simulação. O dashboard exibe o desempenho do modelo de ML ao vivo, mostrando métricas como acurácia, alarmes falsos e riscos não detectados, oferecendo feedback instantâneo sobre a eficácia do "cérebro" preditivo.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Interface Gráfica (GUI):** Tkinter
* **Manipulação de Dados:** Pandas
* **Machine Learning:** Scikit-learn
* **Geração de Gráficos:** Matplotlib & Seaborn
* **Controle de Versão:** Git & GitHub

---

## 📂 Estrutura do Projeto

O código é modularizado para facilitar a manutenção e o entendimento:

-   `config.py`: "Painel de controle" com todos os parâmetros da simulação.
-   `machine.py`: Define o comportamento de uma máquina e seus sensores.
-   `simulator.py`: Orquestra o parque de máquinas e o ciclo de simulação.
-   `logger.py`: Gerencia a criação de diretórios e a escrita de todos os logs.
-   `train_model.py`: Script autônomo para gerar dados e treinar o modelo de ML.
-   `ml_model.py`: Carrega o modelo treinado e serve as previsões para o simulador.
-   `main_app.py`: Ponto de entrada que executa a interface gráfica e inicia a simulação.
-   `report_analyzer_app.py`: Ferramenta de análise visual para os "prontuários" das máquinas que falharam.
