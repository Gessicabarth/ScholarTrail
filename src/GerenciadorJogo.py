import pygame
from src.Const import JANELA_LARGURA, JANELA_ALTURA, JANELA_FPS
from src.TelaMenu import TelaMenu


# --- Gerencia o ciclo de vida do jogo e a tela ativa ---
class GerenciadorJogo:

    def __init__(self):
        pygame.init()
        self.janela = pygame.display.set_mode((JANELA_LARGURA, JANELA_ALTURA))
        pygame.display.set_caption("ScholarTrail")
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.tela_ativa = TelaMenu(self)

    def trocar_tela(self, nova_tela):
        self.tela_ativa = nova_tela

    def executar(self):
        while self.rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                else:
                    self.tela_ativa.processar_evento(evento)

            self.tela_ativa.desenhar(self.janela)
            pygame.display.flip()
            self.relogio.tick(JANELA_FPS)

        pygame.quit()
