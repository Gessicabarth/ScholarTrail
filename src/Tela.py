from abc import ABC, abstractmethod


# --- Classe abstrata base — todas as telas do jogo herdam dela ---
class Tela(ABC):

    @abstractmethod
    def desenhar(self, janela):
        pass

    @abstractmethod
    def processar_evento(self, evento):
        pass

