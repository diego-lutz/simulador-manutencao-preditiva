import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
from simulator import Simulator
from logger import DataLogger
from ml_model import MLModel

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Simulador de Manutenção Preditiva v1.0")
        self.master.geometry("650x450")
        
        self.logger = DataLogger()
        self.ml_model = MLModel(model_path="predictive_model.joblib")
        self.simulator = Simulator(self.logger, self.ml_model)

        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        controls_frame = ttk.LabelFrame(self, text="Controles", padding="10")
        controls_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Ciclos de Simulação (0 para infinito):").pack(side="left", padx=5)
        self.cycles_var = tk.StringVar(value="1000")
        self.cycles_entry = ttk.Entry(controls_frame, textvariable=self.cycles_var, width=10)
        self.cycles_entry.pack(side="left", padx=5)

        self.start_button = ttk.Button(controls_frame, text="Iniciar Simulação", command=self.start_simulation)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = ttk.Button(controls_frame, text="Parar Simulação", command=self.stop_simulation, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True, padx=10)

        status_frame = ttk.LabelFrame(main_frame, text="Status da Simulação", padding="10")
        status_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        performance_frame = ttk.LabelFrame(main_frame, text="Desempenho do ML (Ao Vivo)", padding="10")
        performance_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        self.status_vars = {
            "Ciclo Atual": tk.StringVar(value="0"),
            "Máquinas Ativas": tk.StringVar(value="0"),
            "Total de Falhas": tk.StringVar(value="0")
        }
        for i, (text, var) in enumerate(self.status_vars.items()):
            ttk.Label(status_frame, text=f"{text}:").grid(row=i, column=0, sticky="w", pady=2)
            ttk.Label(status_frame, textvariable=var).grid(row=i, column=1, sticky="e", pady=2)

        self.perf_vars = {
            "Acertos": tk.StringVar(value="0"),
            "Erros": tk.StringVar(value="0"),
            "Alarmes Falsos": tk.StringVar(value="0"),
            "Riscos Perdidos": tk.StringVar(value="0"),
            "Acurácia ao Vivo": tk.StringVar(value="N/A")
        }
        for i, (text, var) in enumerate(self.perf_vars.items()):
            ttk.Label(performance_frame, text=f"{text}:").grid(row=i, column=0, sticky="w", pady=2)
            ttk.Label(performance_frame, textvariable=var).grid(row=i, column=1, sticky="e", pady=2)

        log_frame = ttk.LabelFrame(self, text="Log de Eventos", padding="10")
        log_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=(5,10))
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=5, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log_to_ui(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_simulation(self):
        if not self.ml_model.load():
            self.log_to_ui("ERRO: Falha ao carregar modelo. Execute 'train_model.py' primeiro.")
            return

        self.logger.setup_directories_and_logs()
        
        try:
            total_cycles = int(self.cycles_var.get())
        except ValueError:
            self.log_to_ui("ERRO: Número de ciclos inválido.")
            return

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.cycles_entry.config(state="disabled")
        self.log_to_ui("Iniciando simulação...")

        self.simulation_thread = threading.Thread(
            target=self.simulator.run_simulation_loop,
            args=(total_cycles,),
            daemon=True
        )
        self.simulation_thread.start()
        
        self.update_ui_loop()

    def stop_simulation(self):
        if self.simulator.is_running:
            self.log_to_ui("Sinal de parada enviado. Finalizando o ciclo atual...")
            self.simulator.is_running = False
            self.stop_button.config(state="disabled")

    def update_ui_loop(self):
        if self.simulator.is_running:
            self.status_vars["Ciclo Atual"].set(str(self.simulator.ciclo_atual))
            self.status_vars["Máquinas Ativas"].set(str(len(self.simulator.parque_maquinas)))
            self.status_vars["Total de Falhas"].set(str(self.simulator.total_falhas))
            
            stats = self.simulator.performance_monitor.get_stats()
            self.perf_vars["Acertos"].set(str(stats["acertos"]))
            self.perf_vars["Erros"].set(str(stats["erros"]))
            self.perf_vars["Alarmes Falsos"].set(str(stats["alarmes_falsos"]))
            self.perf_vars["Riscos Perdidos"].set(str(stats["riscos_perdidos"]))
            self.perf_vars["Acurácia ao Vivo"].set(stats["acuracia_vivo"])
            
            self.master.after(1000, self.update_ui_loop)
        else:
            if hasattr(self, 'simulation_thread') and not self.simulation_thread.is_alive():
                self.log_to_ui("Simulação finalizada.")
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.cycles_entry.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()