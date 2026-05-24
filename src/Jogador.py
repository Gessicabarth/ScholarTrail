import pygame
from src.Const import JOGADOR_INTERVALO_PASSO_MS


# --- Representa um jogador no tabuleiro ---
class Jogador:

    def __init__(self, numero, caminho_imagem, posicao_inicial, deslocamento_x=0):
        self.numero = numero
        self.imagem = pygame.image.load(caminho_imagem).convert_alpha()
        self.x, self.y = posicao_inicial
        self.deslocamento_x = deslocamento_x
        self.casa_atual = 0
        self.casas_destino = []
        self.movendo = False
        self.tempo_ultimo_passo = 0

    def iniciar_movimento(self, casas):
        # --- Recebe lista de casas pra percorrer uma a uma ---
        self.casas_destino = casas
        self.movendo = True
        self.tempo_ultimo_passo = pygame.time.get_ticks()

    def atualizar(self):
        # --- Move o jogador casa a casa com intervalo de tempo ---
        if not self.movendo:
            return

        agora = pygame.time.get_ticks()
        if agora - self.tempo_ultimo_passo >= JOGADOR_INTERVALO_PASSO_MS:
            if self.casas_destino:
                proxima = self.casas_destino.pop(0)
                self.x, self.y = proxima.obter_centro()
                self.casa_atual = proxima.numero
                self.tempo_ultimo_passo = agora
            else:
                self.movendo = False

    def desenhar(self, janela, ativo=True):
        # --- Desenha o personagem (transparente se nao for a vez) ---
        imagem = self.imagem.copy()
        if not ativo:
            imagem.set_alpha(100)
        altura_img = imagem.get_height()
        rect = imagem.get_rect(midbottom=(self.x + self.deslocamento_x, self.y + altura_img // 4))
        janela.blit(imagem, rect)
