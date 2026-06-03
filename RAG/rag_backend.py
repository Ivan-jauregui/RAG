import os
import urllib.parse
from dotenv import load_dotenv
import vecs
from sentence_transformers import SentenceTransformer
from groq import Groq

# Cargar variables de entorno
load_dotenv()

class MotorRAG:
    def __init__(self):
        """Inicializa las conexiones solo cuando se crea la clase."""
        self.password = urllib.parse.quote_plus(os.getenv("SUPABASE_PASSWORD"))
        self.db_connection = f"postgresql://postgres.oskxjbviwrjyaymzinct:{self.password}@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
        
        self.vx = vecs.create_client(self.db_connection)
        self.docs = self.vx.get_or_create_collection(name="rag_bdd2", dimension=384)
        
        try:
            self.docs.create_index(measure="cosine_distance", replace=False)
        except Exception as e:
            if "already exists" in str(e) or "replace is set to False" in str(e):
                print("El índice ya existe en Supabase.")
            else:
                raise e

        
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

    def procesar_e_ingestar_texto(self, text, chunk_size=60, overlap=15):
        """Función de un solo uso para cargar datos a Supabase."""
        words = text.split()
        chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]
        
        for i, texto_chunk in enumerate(chunks):
            vector = self.modelo_embedding.encode(texto_chunk).tolist()
            self.docs.upsert(records=[(f"chunk_dinamico_{i}", vector, {"texto": texto_chunk})])
        return len(chunks)

    def consultar(self, pregunta):
        """Busca el contexto y le pregunta al LLM."""
        # 1. Obtener contexto
        vector_pregunta = self.modelo_embedding.encode(pregunta).tolist()
        resultados = self.docs.query(data=vector_pregunta, limit=3, include_metadata=True)
        contexto = "\n\n".join([res[1]["texto"] for res in resultados])

        # 2. Configurar LLM
        prompt_sistema = "Eres un asistente experto en Bases de Datos..."
        prompt_usuario = f"Contexto:\n{contexto}\n\nPregunta: {pregunta}"

        # 3. Llamar a Groq
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content