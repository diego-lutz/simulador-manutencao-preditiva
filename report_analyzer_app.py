import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import glob
import os


try:
    from config import CATALOGO_MAQUINAS, FASES_SAUDE
except ImportError:
    print("ERRO: Não foi possível encontrar o arquivo 'config.py'.")
    print("Certifique-se de que todos os arquivos do projeto estão na mesma pasta.")
    CATALOGO_MAQUINAS = {}
    FASES_SAUDE = {"Normal": 0, "Alerta": 1, "Risco_Iminente": 2, "Falha": 3}


class ReportAnalyzerApp(tk.Frame):
    """
    Uma aplicação de GUI para carregar, visualizar e analisar os relatórios
    de falha gerados pelo simulador.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Analisador de Relatórios de Falha")
        self.master.geometry("1000x800")
        
        self.report_files = []
        self.current_file_index = -1
        
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # --- Frame de Controles Superior ---
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        self.select_folder_button = ttk.Button(top_frame, text="Selecionar Pasta de Relatórios", command=self.select_folder)
        self.select_folder_button.pack(side="left")
        
        self.current_file_label = ttk.Label(top_frame, text="Nenhum arquivo carregado", font=("Arial", 10, "italic"))
        self.current_file_label.pack(side="left", padx=20)
        
        self.next_file_button = ttk.Button(top_frame, text="Próximo Arquivo  >>", command=self.load_next_file, state="disabled")
        self.next_file_button.pack(side="right")
        
        # --- Frame Principal para o Gráfico ---
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Configuração inicial do canvas do Matplotlib
        self.fig, self.ax = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.tight_layout(pad=3.0)

    def select_folder(self):
        """Abre uma caixa de diálogo para o usuário selecionar uma pasta."""
        folder_path = filedialog.askdirectory(initialdir="logs/archived_data/failure_reports", title="Selecione a pasta 'failure_reports'")
        if not folder_path:
            return
            
        # Encontra todos os arquivos CSV na pasta selecionada
        self.report_files = sorted(glob.glob(os.path.join(folder_path, "report_*.csv")))
        
        if not self.report_files:
            self.current_file_label.config(text=f"Nenhum arquivo .csv encontrado em '{os.path.basename(folder_path)}'")
            self.next_file_button.config(state="disabled")
            return
            
        self.current_file_index = -1
        self.next_file_button.config(state="normal")
        self.load_next_file()

    def load_next_file(self):
        """Carrega e exibe o próximo arquivo da lista de relatórios."""
        if not self.report_files:
            return
            
        self.current_file_index = (self.current_file_index + 1) % len(self.report_files)
        filepath = self.report_files[self.current_file_index]
        
        filename = os.path.basename(filepath)
        self.current_file_label.config(text=f"Analisando: {filename}", font=("Arial", 10, "bold"))
        
        try:
            df = pd.read_csv(filepath)
            self.plot_report(df)
        except Exception as e:
            print(f"Erro ao ler ou plotar o arquivo {filename}: {e}")
            self.current_file_label.config(text=f"Erro ao carregar {filename}", font=("Arial", 10, "italic"))


    def get_phase_spans(self, df, phase_num):
        """Encontra os blocos de início e fim para uma determinada fase."""
        spans = []
        in_span = False
        start_index = 0
        for index, row in df.iterrows():
            is_in_phase = (row['health_phase'] == phase_num)
            if is_in_phase and not in_span:
                start_index = index
                in_span = True
            elif not is_in_phase and in_span:
                spans.append((start_index, index -1))
                in_span = False
        if in_span: # Garante que o último bloco seja adicionado
            spans.append((start_index, df.index[-1]))
        return spans

    def plot_report(self, df):
        """
        Gera os gráficos aprimorados com os dados do relatório da máquina,
        incluindo marcadores de evento e anotações de duração.
        """
        for axis in self.ax:
            axis.clear()
            
        phase_names = {v: k for k, v in FASES_SAUDE.items()}
        df['tempo'] = df.index

        # --- Gráfico 1: Temperatura do Óleo ---
        sensor_id = "temp_oleo"
        config_sensor = next((s for s in CATALOGO_MAQUINAS["Prensa Hidráulica PH-300T"]["sensores_config"] if s["sensor_id"] == sensor_id), None)
        if config_sensor:
            normal_range = config_sensor["faixa_normal"]
            self.ax[0].axhspan(normal_range[0], normal_range[1], color='green', alpha=0.2, label='Faixa Normal')
        self.ax[0].plot(df['tempo'], df[sensor_id], label=sensor_id, color='orangered', zorder=10)
        self.ax[0].set_title("Temperatura do Óleo (°C)")
        self.ax[0].grid(True, linestyle='--', alpha=0.6)

        # --- Gráfico 2: Vibração do Motor ---
        sensor_id = "vibracao_motor"
        config_sensor = next((s for s in CATALOGO_MAQUINAS["Prensa Hidráulica PH-300T"]["sensores_config"] if s["sensor_id"] == sensor_id), None)
        if config_sensor:
            normal_range = config_sensor["faixa_normal"]
            self.ax[1].axhspan(normal_range[0], normal_range[1], color='green', alpha=0.2, label='Faixa Normal')
        self.ax[1].plot(df['tempo'], df[sensor_id], label=sensor_id, color='purple', zorder=10)
        self.ax[1].set_title("Vibração do Motor (mm/s)")
        self.ax[1].grid(True, linestyle='--', alpha=0.6)
        
        # --- Gráfico 3: Degradação Interna ---
        self.ax[2].plot(df['tempo'], df['fator_desgaste'], label='Fator de Desgaste', color='black', linestyle='--')
        self.ax[2].set_title("Degradação Interna da Máquina")
        self.ax[2].set_ylabel("Fator de Desgaste")
        self.ax[2].set_xlabel("Tempo de Operação (Horas)")
        self.ax[2].grid(True, linestyle='--', alpha=0.6)
        
        # --- APRIMORAMENTO 1: Marcadores de Evento ---
        eventos_degradacao = df[df['volatilidade_vibracao'].diff() > 0.1]
        is_first_event = True
        for index in eventos_degradacao.index:
            label = "Evento de Degradação" if is_first_event else ""
            for axis in self.ax:
                axis.axvline(x=index, color='red', linestyle='--', linewidth=1.5, label=label, zorder=15)
            is_first_event = False

        # --- APRIMORAMENTO 2: Coloração de Fundo e Duração ---
        phase_colors = {0: 'lightgreen', 1: 'gold', 2: 'salmon'}
        phase_durations = df['health_phase'].value_counts().to_dict()

        for phase_num, phase_name in phase_names.items():
            if phase_num in phase_colors:
                for start, end in self.get_phase_spans(df, phase_num):
                    for axis in self.ax:
                        axis.axvspan(start, end, color=phase_colors[phase_num], alpha=0.3, ec=None, zorder=1)
                    
                    duration = phase_durations.get(phase_num, 0)
                    text_x = start + (end - start) / 2
                    text_y_pos = self.ax[0].get_ylim()[0] + (self.ax[0].get_ylim()[1] - self.ax[0].get_ylim()[0]) * 0.95
                    self.ax[0].text(text_x, text_y_pos, f"{phase_name}\n{duration} horas", 
                                    ha='center', va='top', fontsize=9, weight='bold',
                                    bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='black', lw=1, alpha=0.7))

        # --- Finalização e Legendas ---
        self.fig.suptitle(f"Análise de Ciclo de Vida: Máquina {df['machine_id'].iloc[0]}", fontsize=16, weight='bold')
        for axis in self.ax:
            handles, labels = axis.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            axis.legend(by_label.values(), by_label.keys(), loc='upper left')
            
        self.fig.tight_layout(pad=3.0, rect=[0, 0, 1, 0.96])
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportAnalyzerApp(master=root)
    app.mainloop()