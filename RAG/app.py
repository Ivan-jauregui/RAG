import customtkinter as ctk
import threading
from rag_backend import MotorRAG

class AppRAG(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Asistente RAG Profesional")
        self.geometry("600x500")
        
        self.motor = MotorRAG()
        
        self.construir_interfaz()

    def construir_interfaz(self):
        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="RAG", font=("Arial", 18, "bold"))
        self.lbl_titulo.pack(pady=10)

        # Input de pregunta
        self.entrada_pregunta = ctk.CTkEntry(self, placeholder_text="Escribe tu pregunta aquí...", width=400)
        self.entrada_pregunta.pack(pady=10)

        # Botón de búsqueda
        self.btn_preguntar = ctk.CTkButton(self, text="Preguntar", command=self.evento_preguntar)
        self.btn_preguntar.pack(pady=10)

        # Caja de texto para la respuesta
        self.caja_respuesta = ctk.CTkTextbox(self, width=500, height=300, wrap="word")
        self.caja_respuesta.pack(pady=10)
        self.caja_respuesta.insert("0.0", "Las respuestas aparecerán aquí...")
        self.caja_respuesta.configure(state="disabled") 

    def evento_preguntar(self):
        pregunta = self.entrada_pregunta.get()
        if not pregunta.strip():
            return

        self.actualizar_texto_respuesta("Buscando al y consultando al modelo...")
        self.btn_preguntar.configure(state="disabled")

        hilo = threading.Thread(target=self.tarea_en_segundo_plano, args=(pregunta,))
        hilo.start()

    def tarea_en_segundo_plano(self, pregunta):
        try:
            respuesta_llm = self.motor.consultar(pregunta)
            self.actualizar_texto_respuesta(respuesta_llm)
        except Exception as e:
            self.actualizar_texto_respuesta(f"Ocurrió un error: {e}")
        finally:
            self.btn_preguntar.configure(state="normal")

    def actualizar_texto_respuesta(self, texto):
        self.caja_respuesta.configure(state="normal")
        self.caja_respuesta.delete("0.0", "end")
        self.caja_respuesta.insert("0.0", texto)
        self.caja_respuesta.configure(state="disabled")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = AppRAG()
    app.mainloop()