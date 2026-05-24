import pygame
from src.Tela import Tela
from src.Const import (
    JANELA_LARGURA, JANELA_ALTURA,
    FONTE_TITULO,
    MENU_FONTE_TITULO_TAMANHO, MENU_FONTE_OPCAO_TAMANHO,
    MENU_FONTE_OPCAO_SELECIONADA_TAMANHO, MENU_FONTE_CONTROLES_TAMANHO,
    COR_TITULO_MENU, COR_SOMBRA_MENU, COR_OPCAO_DESTAQUE_MENU,
    COR_BRANCA, COR_PRETA
)
from src.Tabuleiro import Tabuleiro


# --- Tela do menu principal ---
class TelaMenu(Tela):

    def __init__(self, jogo):
        # --- Janela, opcoes e fontes ---
        self.jogo = jogo
        self.opcoes = ["Jogar - 1 Jogador", "Jogar - 2 Jogadores", "Sair"]
        self.opcao_selecionada = 0
        self.fundo = pygame.image.load("asset/imagem/fundo_menu_modo_claro.png").convert()
        self.fonte_titulo = pygame.font.SysFont(FONTE_TITULO, MENU_FONTE_TITULO_TAMANHO, bold=True)
        self.fonte_opcao_padrao = pygame.font.SysFont(FONTE_TITULO, MENU_FONTE_OPCAO_TAMANHO, bold=True)
        self.fonte_opcao_selecionada = pygame.font.SysFont(FONTE_TITULO, MENU_FONTE_OPCAO_SELECIONADA_TAMANHO, bold=True)
        self.fonte_controles = pygame.font.SysFont(FONTE_TITULO, MENU_FONTE_CONTROLES_TAMANHO)
        
        # --- Som do menu ---
        pygame.mixer.music.load("asset/som/som_menu.wav")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def desenhar(self, janela):
        # --- Fundo ---
        janela.blit(self.fundo, (0, 0))

        # --- Título com sombra em camadas ---
        for deslocamento in [(3, 3), (2, 2), (-1, -1)]:
            sombra = self.fonte_titulo.render("Scholar Trail", True, COR_SOMBRA_MENU)
            janela.blit(sombra, sombra.get_rect(center=(JANELA_LARGURA // 2 + deslocamento[0], 100 + deslocamento[1])))
        titulo = self.fonte_titulo.render("Scholar Trail", True, COR_TITULO_MENU)
        janela.blit(titulo, titulo.get_rect(center=(JANELA_LARGURA // 2, 100)))

        # --- Opções com destaque na selecionada ---
        for indice, opcao in enumerate(self.opcoes):
            if indice == self.opcao_selecionada:
                fonte = self.fonte_opcao_selecionada
                cor = COR_OPCAO_DESTAQUE_MENU
                cor_sombra = COR_SOMBRA_MENU
                deslocamento_sombra = 3
            else:
                fonte = self.fonte_opcao_padrao
                cor = COR_BRANCA
                cor_sombra = COR_PRETA
                deslocamento_sombra = 2

            posicao_y = 320 + (indice * 80)
            sombra = fonte.render(opcao, True, cor_sombra)
            janela.blit(sombra, sombra.get_rect(center=(JANELA_LARGURA // 2 + deslocamento_sombra, posicao_y + deslocamento_sombra)))
            texto = fonte.render(opcao, True, cor)
            janela.blit(texto, texto.get_rect(center=(JANELA_LARGURA // 2, posicao_y)))

        # --- Informativo de controles ---
        controles_texto = "Rolar dado: ESPACO | Navegar: SETAS | Confirmar: ENTER"
        sombra = self.fonte_controles.render(controles_texto, True, COR_PRETA)
        janela.blit(sombra, sombra.get_rect(center=(JANELA_LARGURA // 2 + 2, JANELA_ALTURA - 25 + 2)))
        controles = self.fonte_controles.render(controles_texto, True, COR_BRANCA)
        janela.blit(controles, controles.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA - 25)))

    def processar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)
            elif evento.key == pygame.K_DOWN:
                self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirmar_opcao()

    def confirmar_opcao(self):
        if self.opcao_selecionada == 0:
            self.jogo.trocar_tela(Tabuleiro(self.jogo, 1))
        elif self.opcao_selecionada == 1:
            self.jogo.trocar_tela(Tabuleiro(self.jogo, 2))
        elif self.opcao_selecionada == 2:
            self.jogo.rodando = False
