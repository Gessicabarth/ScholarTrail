import json
import random


# --- Gerencia as perguntas do quiz ---
class GerenciadorQuiz:

    def __init__(self, caminho_json="perguntasQuiz.json"):
        self.perguntas = self.carregar_perguntas(caminho_json)
        self.perguntas_usadas = []

    def carregar_perguntas(self, caminho):
        # --- Carrega todas as perguntas do arquivo JSON ---
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def sortear_pergunta(self):
        # --- Sorteia uma pergunta que ainda nao foi usada ---
        disponiveis = [p for p in self.perguntas if p["id"] not in self.perguntas_usadas]
        if not disponiveis:
            self.perguntas_usadas = []
            disponiveis = self.perguntas

        pergunta = random.choice(disponiveis)
        self.perguntas_usadas.append(pergunta["id"])
        return pergunta

    def verificar_resposta(self, pergunta, resposta):
        # --- Verifica se a resposta esta correta ---
        return resposta == pergunta["resposta_correta"]
