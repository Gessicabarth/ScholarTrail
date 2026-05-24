import pygame
from src.Const import (
    CASA_LARGURA, CASA_ALTURA, CASA_BORDA_RAIO, CASA_ESPESSURA_BORDA,
    COR_VIDRO_CLARO, COR_BORDA_CLARO, COR_NUMERO_CASA_CLARO
)


# --- Representa uma casa individual do tabuleiro ---
class CasaTabuleiro:

    def __init__(self, numero, coluna, linha):
        self.numero = numero
        self.coluna = coluna
        self.linha = linha
        self.x = 0
        self.y = 0

    def calcular_posicao(self, offset_x, offset_y):
        # --- Calcula a posicao em pixels baseado na coluna e linha ---
        self.x = offset_x + self.coluna * CASA_LARGURA
        self.y = offset_y + self.linha * CASA_ALTURA

    def desenhar(self, janela):
        # --- Fundo da casa com transparencia ---
        superficie = pygame.Surface((CASA_LARGURA, CASA_ALTURA), pygame.SRCALPHA)
        pygame.draw.rect(superficie, COR_VIDRO_CLARO, (0, 0, CASA_LARGURA, CASA_ALTURA), border_radius=CASA_BORDA_RAIO)
        pygame.draw.rect(superficie, COR_BORDA_CLARO, (0, 0, CASA_LARGURA, CASA_ALTURA), CASA_ESPESSURA_BORDA, border_radius=CASA_BORDA_RAIO)
        janela.blit(superficie, (self.x, self.y))

        # --- Numero da casa ---
        fonte = pygame.font.SysFont("Arial", 20, bold=True)
        texto = fonte.render(str(self.numero), True, COR_NUMERO_CASA_CLARO)
        retangulo = texto.get_rect(center=(self.x + CASA_LARGURA // 2, self.y + CASA_ALTURA // 2))
        janela.blit(texto, retangulo)

    def obter_centro(self):
        # --- Retorna o centro da casa em pixels ---
        return (self.x + CASA_LARGURA // 2, self.y + CASA_ALTURA // 2)
