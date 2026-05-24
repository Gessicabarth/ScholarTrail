import random
import pygame
from src.Tela import Tela
from src.CasaTabuleiro import CasaTabuleiro
from src.Jogador import Jogador
from src.GerenciadorQuiz import GerenciadorQuiz
from src.Const import (
    JANELA_LARGURA, JANELA_ALTURA, CASA_LARGURA, CASA_ALTURA,
    JOGADOR_DESLOCAMENTO_HORIZONTAL,
    DADO_VALOR_MINIMO, DADO_VALOR_MAXIMO,
    DELAY_ENTRE_TURNOS_MS, DERROTA_LIMITE_RODADAS,
    QUIZ_COR_FUNDO_PAINEL, QUIZ_COR_BORDA_PAINEL, QUIZ_COR_DISCIPLINA,
    QUIZ_COR_OPCAO_NORMAL, QUIZ_COR_OPCAO_SELECIONADA,
    QUIZ_COR_ACERTO, QUIZ_COR_ERRO,
    QUIZ_FONTE, QUIZ_FONTE_TAMANHO, QUIZ_FONTE_FEEDBACK_TAMANHO,
    QUIZ_LARGURA_PAINEL, QUIZ_ALTURA_PAINEL,
    QUIZ_ESPESSURA_BORDA, QUIZ_RAIO_BORDA,
    QUIZ_DURACAO_FEEDBACK_MS, QUIZ_DELAY_ANTES_ABRIR_MS
)


# --- Tela do tabuleiro de jogo ---
class Tabuleiro(Tela):

    def __init__(self, jogo, quantidade_jogadores):
        self.jogo = jogo
        self.quantidade_jogadores = quantidade_jogadores
        self.fundo = pygame.image.load("asset/imagem/fundo_tabuleiro_modo_claro.png").convert()
        # --- Som do tabuleiro ---
        pygame.mixer.music.load("asset/som/som_tabuleiro.wav")
        pygame.mixer.music.play(-1)
        self.casas = self.criar_casas()
        self.pos_partida = self.calcular_pos_partida()
        self.pos_chegada = self.calcular_pos_chegada()
        self.jogadores = self.criar_jogadores()
        self.turno = 0
        self.valor_dado = 0
        self.aguardando_turno = False
        self.tempo_fim_movimento = 0

        # --- Quiz ---
        self.quiz = GerenciadorQuiz()
        self.quiz_ativo = False
        self.quiz_pergunta = None
        self.quiz_opcao_selecionada = 0
        self.quiz_feedback = None
        self.quiz_tempo_feedback = 0
        self.quiz_aguardando = False
        self.quiz_tempo_aguardando = 0
        self.quiz_casa_anterior = 0
        self.quiz_voltar = False
        self.casas_com_quiz = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        self.vencedor = None
        self.rodada_atual = 0
        self.derrota = False

    def criar_casas(self):
        # --- Caminho em formato cobra ---
        ordem_do_caminho = [
            (0, 0), (1, 0), (2, 0),
            (2, 1), (2, 2),
            (1, 2), (0, 2),
            (0, 3), (0, 4), (0, 5), (0, 6),
            (1, 6), (2, 6), (2, 5), (2, 4),
            (3, 4), (4, 4),
            (4, 3), (4, 2), (4, 1), (4, 0),
            (5, 0), (6, 0),
            (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
            (5, 6),
        ]

        # --- Centraliza o caminho na tela com deslocamento pra direita ---
        max_coluna = max(c for c, l in ordem_do_caminho)
        max_linha = max(l for c, l in ordem_do_caminho)
        largura_total = (max_coluna + 1) * CASA_LARGURA
        altura_total = (max_linha + 1) * CASA_ALTURA
        self.offset_x = (JANELA_LARGURA - largura_total) // 2 + 100
        self.offset_y = (JANELA_ALTURA - altura_total) // 2 + 30

        casas = []
        for i, (coluna, linha) in enumerate(ordem_do_caminho):
            casa = CasaTabuleiro(i + 1, coluna, linha)
            casa.calcular_posicao(self.offset_x, self.offset_y)
            casas.append(casa)

        return casas

    def criar_jogadores(self):
        # --- Cria os jogadores na posicao de partida com deslocamento horizontal ---
        jogadores = []
        deslocamentos = [-15, 15]
        for i in range(self.quantidade_jogadores):
            caminho_imagem = f"asset/imagem/personagem_{i + 1:02d}.png"
            x = self.pos_partida[0] + (i * JOGADOR_DESLOCAMENTO_HORIZONTAL)
            y = self.pos_partida[1]
            deslocamento = deslocamentos[i] if self.quantidade_jogadores > 1 else 0
            jogador = Jogador(i + 1, caminho_imagem, (x, y), deslocamento)
            jogadores.append(jogador)
        return jogadores

    def calcular_pos_partida(self):
        # --- Posicao da partida: a esquerda da casa 1, mesma altura ---
        casa1 = self.casas[0]
        x = casa1.x - 80
        y = casa1.y + CASA_ALTURA // 2
        return (x, y)

    def calcular_pos_chegada(self):
        # --- Posicao da chegada: entre as casas 30 e 13 ---
        casa30 = self.casas[29]
        casa13 = self.casas[12]
        x = (casa30.x + casa13.x + CASA_LARGURA) // 2
        y = casa30.y + CASA_ALTURA // 2
        return (x, y)

    def jogador_da_vez(self):
        return self.jogadores[self.turno]

    def algum_jogador_movendo(self):
        return any(j.movendo for j in self.jogadores)

    def rolar_dado(self):
        # --- Rola o dado e move o jogador da vez ---
        jogador = self.jogador_da_vez()
        self.valor_dado = random.randint(DADO_VALOR_MINIMO, DADO_VALOR_MAXIMO)
        self.quiz_casa_anterior = jogador.casa_atual

        # --- Conta rodada no modo solo ---
        if self.quantidade_jogadores == 1:
            self.rodada_atual += 1

        # --- Calcula casas a percorrer ---
        casa_inicio = jogador.casa_atual
        casa_fim = casa_inicio + self.valor_dado
        casas_percurso = self.casas[casa_inicio:casa_fim]

        jogador.iniciar_movimento(casas_percurso)

    def passar_turno(self):
        self.turno = (self.turno + 1) % self.quantidade_jogadores

    def abrir_quiz(self):
        # --- Abre o painel de quiz ---
        self.quiz_ativo = True
        self.quiz_pergunta = self.quiz.sortear_pergunta()
        self.quiz_opcao_selecionada = 0
        self.quiz_feedback = None

    def confirmar_resposta(self):
        # --- Verifica a resposta e da feedback ---
        resposta = str(self.quiz_opcao_selecionada + 1)
        acertou = self.quiz.verificar_resposta(self.quiz_pergunta, resposta)

        if acertou:
            self.quiz_feedback = "Acertou! Permanece na casa."
            self.quiz_voltar = False
        else:
            self.quiz_feedback = "Errou! Voltando..."
            self.quiz_voltar = True

        self.quiz_tempo_feedback = pygame.time.get_ticks()

    def voltar_jogador(self):
        # --- Teleporta o jogador de volta pra casa anterior ---
        jogador = self.jogador_da_vez()
        if self.quiz_casa_anterior > 0:
            casa_volta = self.casas[self.quiz_casa_anterior - 1]
            jogador.x, jogador.y = casa_volta.obter_centro()
            jogador.casa_atual = self.quiz_casa_anterior
        else:
            jogador.x, jogador.y = self.pos_partida
            jogador.casa_atual = 0

    def quebrar_texto(self, texto, fonte, largura_maxima):
        # --- Quebra o texto em linhas que cabem na largura maxima ---
        palavras = texto.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + " " + palavra if linha_atual else palavra
            if fonte.size(teste)[0] <= largura_maxima:
                linha_atual = teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def desenhar_quiz(self, janela):
        # --- Painel escuro centralizado com borda rosa ---
        painel = pygame.Surface((QUIZ_LARGURA_PAINEL, QUIZ_ALTURA_PAINEL), pygame.SRCALPHA)
        pygame.draw.rect(painel, QUIZ_COR_FUNDO_PAINEL, (0, 0, QUIZ_LARGURA_PAINEL, QUIZ_ALTURA_PAINEL), border_radius=QUIZ_RAIO_BORDA)
        pygame.draw.rect(painel, QUIZ_COR_BORDA_PAINEL, (0, 0, QUIZ_LARGURA_PAINEL, QUIZ_ALTURA_PAINEL), QUIZ_ESPESSURA_BORDA, border_radius=QUIZ_RAIO_BORDA)
        x = (JANELA_LARGURA - QUIZ_LARGURA_PAINEL) // 2
        y = (JANELA_ALTURA - QUIZ_ALTURA_PAINEL) // 2
        janela.blit(painel, (x, y))

        margem = 40
        largura_texto = QUIZ_LARGURA_PAINEL - margem * 2

        # --- Disciplina (rosa, bold, alinhada a esquerda) ---
        fonte_disciplina = pygame.font.SysFont(QUIZ_FONTE, QUIZ_FONTE_TAMANHO, bold=True)
        texto_disciplina = fonte_disciplina.render(self.quiz_pergunta["disciplina"], True, QUIZ_COR_DISCIPLINA)
        janela.blit(texto_disciplina, (x + margem, y + 25))

        # --- Pergunta (bold, com quebra de linha, alinhada a esquerda) ---
        fonte_pergunta = pygame.font.SysFont(QUIZ_FONTE, QUIZ_FONTE_TAMANHO, bold=True)
        linhas_pergunta = self.quebrar_texto(self.quiz_pergunta["pergunta"], fonte_pergunta, largura_texto)
        for j, linha in enumerate(linhas_pergunta):
            texto_linha = fonte_pergunta.render(linha, True, (255, 255, 255))
            janela.blit(texto_linha, (x + margem, y + 80 + j * 28))

        # --- Opcoes (com quebra de linha, alinhadas a esquerda) ---
        fonte_opcao = pygame.font.SysFont(QUIZ_FONTE, QUIZ_FONTE_TAMANHO)
        opcoes = self.quiz_pergunta["opcoes"]
        pos_y = y + 60 + len(linhas_pergunta) * 28 + 40
        for i, (chave, texto_opcao) in enumerate(opcoes.items()):
            if i == self.quiz_opcao_selecionada:
                cor = QUIZ_COR_OPCAO_SELECIONADA
            else:
                cor = QUIZ_COR_OPCAO_NORMAL
            texto_completo = f"{chave}. {texto_opcao}"
            linhas_opcao = self.quebrar_texto(texto_completo, fonte_opcao, largura_texto)
            for j, linha in enumerate(linhas_opcao):
                texto = fonte_opcao.render(linha, True, cor)
                janela.blit(texto, (x + margem, pos_y))
                pos_y += 25
            pos_y += 8

        # --- Feedback ou informativo no final do painel, centralizado ---
        if self.quiz_feedback:
            fonte_feedback = pygame.font.SysFont(QUIZ_FONTE, QUIZ_FONTE_FEEDBACK_TAMANHO, bold=True)
            if not self.quiz_voltar:
                texto = fonte_feedback.render(self.quiz_feedback, True, QUIZ_COR_ACERTO)
            else:
                texto = fonte_feedback.render(self.quiz_feedback, True, QUIZ_COR_ERRO)
            rect = texto.get_rect(center=(JANELA_LARGURA // 2, y + QUIZ_ALTURA_PAINEL - 30))
            janela.blit(texto, rect)
        else:
            fonte_info = pygame.font.SysFont(QUIZ_FONTE, QUIZ_FONTE_TAMANHO, bold=True)
            info = fonte_info.render("Setas: navegar | Enter: confirmar", True, QUIZ_COR_OPCAO_NORMAL)
            rect_info = info.get_rect(center=(JANELA_LARGURA // 2, y + QUIZ_ALTURA_PAINEL - 25))
            janela.blit(info, rect_info)

    def desenhar(self, janela):
        # --- Fundo ---
        janela.blit(self.fundo, (0, 0))

        # --- Atualiza logica ---
        for jogador in self.jogadores:
            jogador.atualizar()
        self.atualizar_turno()

        # --- Casas ---
        for casa in self.casas:
            casa.desenhar(janela)

        # --- Jogadores ---
        for i, jogador in enumerate(self.jogadores):
            ativo = (i == self.turno)
            jogador.desenhar(janela, ativo)

        # --- Valor do dado ---
        if self.valor_dado > 0:
            fonte = pygame.font.SysFont("Arial", 36, bold=True)
            texto = fonte.render(f"Dado: {self.valor_dado}", True, (255, 255, 255))
            janela.blit(texto, (20, 20))

        # --- Indicador de vez (so com 2 jogadores) ---
        if self.quantidade_jogadores > 1 and not self.vencedor:
            barra = pygame.Surface((JANELA_LARGURA, 36), pygame.SRCALPHA)
            barra.fill((0, 0, 0, 120))
            janela.blit(barra, (0, JANELA_ALTURA - 36))
            fonte_vez = pygame.font.SysFont("Arial", 20, bold=True)
            jogador = self.jogador_da_vez()
            texto_vez = fonte_vez.render(f"Vez: Jogador {jogador.numero}", True, (255, 255, 255))
            rect_vez = texto_vez.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA - 18))
            janela.blit(texto_vez, rect_vez)
            # --- Mensagem de acao ---
            if not self.algum_jogador_movendo() and not self.aguardando_turno and not self.quiz_ativo and not self.quiz_aguardando:
                fonte_msg = pygame.font.SysFont("Arial", 20, bold=True)
                msg = fonte_msg.render("Pressione ESPACO para rolar o dado", True, (255, 255, 255))
                rect_msg = msg.get_rect(midleft=(20, JANELA_ALTURA - 18))
                janela.blit(msg, rect_msg)

        # --- Barra inferior com rodadas (so modo solo) ---
        if self.quantidade_jogadores == 1 and not self.vencedor and not self.derrota:
            barra = pygame.Surface((JANELA_LARGURA, 36), pygame.SRCALPHA)
            barra.fill((0, 0, 0, 120))
            janela.blit(barra, (0, JANELA_ALTURA - 36))
            fonte_rodada = pygame.font.SysFont("Arial", 20, bold=True)
            texto_rodada = fonte_rodada.render(f"Rodada {self.rodada_atual}/{DERROTA_LIMITE_RODADAS}", True, (255, 255, 255))
            rect_rodada = texto_rodada.get_rect(midright=(JANELA_LARGURA - 20, JANELA_ALTURA - 18))
            janela.blit(texto_rodada, rect_rodada)
            # --- Mensagem de acao ---
            if not self.algum_jogador_movendo() and not self.aguardando_turno and not self.quiz_ativo and not self.quiz_aguardando:
                fonte_msg = pygame.font.SysFont("Arial", 20, bold=True)
                msg = fonte_msg.render("Pressione ESPACO para rolar o dado", True, (255, 255, 255))
                rect_msg = msg.get_rect(midleft=(20, JANELA_ALTURA - 18))
                janela.blit(msg, rect_msg)

        # --- Mensagem de vitoria ---
        if self.vencedor:
            painel_vitoria = pygame.Surface((500, 150), pygame.SRCALPHA)
            pygame.draw.rect(painel_vitoria, QUIZ_COR_FUNDO_PAINEL, (0, 0, 500, 150), border_radius=QUIZ_RAIO_BORDA)
            pygame.draw.rect(painel_vitoria, QUIZ_COR_ACERTO, (0, 0, 500, 150), QUIZ_ESPESSURA_BORDA, border_radius=QUIZ_RAIO_BORDA)
            rect_painel = painel_vitoria.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2))
            janela.blit(painel_vitoria, rect_painel)
            fonte_vitoria = pygame.font.SysFont(QUIZ_FONTE, 48, bold=True)
            texto_vitoria = fonte_vitoria.render(f"Jogador {self.vencedor.numero} venceu!", True, QUIZ_COR_ACERTO)
            rect = texto_vitoria.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2 - 15))
            janela.blit(texto_vitoria, rect)
            fonte_instrucao = pygame.font.SysFont(QUIZ_FONTE, 20)
            instrucao = fonte_instrucao.render("Esc: voltar ao menu", True, (200, 200, 200))
            rect_instrucao = instrucao.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2 + 35))
            janela.blit(instrucao, rect_instrucao)

        # --- Mensagem de derrota ---
        if self.derrota:
            painel_derrota = pygame.Surface((500, 150), pygame.SRCALPHA)
            pygame.draw.rect(painel_derrota, QUIZ_COR_FUNDO_PAINEL, (0, 0, 500, 150), border_radius=QUIZ_RAIO_BORDA)
            pygame.draw.rect(painel_derrota, QUIZ_COR_ERRO, (0, 0, 500, 150), QUIZ_ESPESSURA_BORDA, border_radius=QUIZ_RAIO_BORDA)
            rect_painel = painel_derrota.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2))
            janela.blit(painel_derrota, rect_painel)
            fonte_derrota = pygame.font.SysFont(QUIZ_FONTE, 42, bold=True)
            texto_derrota = fonte_derrota.render("Rodadas esgotadas!", True, QUIZ_COR_ERRO)
            rect = texto_derrota.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2 - 15))
            janela.blit(texto_derrota, rect)
            fonte_instrucao = pygame.font.SysFont(QUIZ_FONTE, 20)
            instrucao = fonte_instrucao.render("Esc: voltar ao menu", True, (200, 200, 200))
            rect_instrucao = instrucao.get_rect(center=(JANELA_LARGURA // 2, JANELA_ALTURA // 2 + 35))
            janela.blit(instrucao, rect_instrucao)

        # --- Quiz ---
        if self.quiz_ativo:
            self.desenhar_quiz(janela)
            # --- Fecha o feedback apos o tempo ---
            if self.quiz_feedback:
                if pygame.time.get_ticks() - self.quiz_tempo_feedback >= QUIZ_DURACAO_FEEDBACK_MS:
                    self.quiz_ativo = False
                    if self.quiz_voltar:
                        self.voltar_jogador()
                        self.quiz_voltar = False
                    self.quiz_feedback = None
                    self.aguardando_turno = True
                    self.tempo_fim_movimento = pygame.time.get_ticks()

        # --- Aguardando quiz abrir ---
        if self.quiz_aguardando:
            if pygame.time.get_ticks() - self.quiz_tempo_aguardando >= QUIZ_DELAY_ANTES_ABRIR_MS:
                self.quiz_aguardando = False
                self.abrir_quiz()

    def processar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if self.quiz_ativo and not self.quiz_feedback:
                # --- Navegacao do quiz ---
                if evento.key == pygame.K_UP:
                    self.quiz_opcao_selecionada = (self.quiz_opcao_selecionada - 1) % 4
                elif evento.key == pygame.K_DOWN:
                    self.quiz_opcao_selecionada = (self.quiz_opcao_selecionada + 1) % 4
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.confirmar_resposta()
            elif not self.quiz_ativo:
                if evento.key == pygame.K_ESCAPE:
                    from src.TelaMenu import TelaMenu
                    self.jogo.trocar_tela(TelaMenu(self.jogo))
                elif evento.key == pygame.K_SPACE:
                    if not self.algum_jogador_movendo() and not self.aguardando_turno and not self.quiz_aguardando and not self.vencedor and not self.derrota:
                        self.rolar_dado()

    def atualizar_turno(self):
        # --- Verifica se o jogador terminou de mover e inicia o quiz ---
        jogador = self.jogador_da_vez()

        # --- Verifica vitoria: jogador passou da ultima casa ---
        if not jogador.movendo and jogador.casa_atual == len(self.casas) and not self.vencedor:
            destino_original = self.quiz_casa_anterior + self.valor_dado
            if destino_original > len(self.casas):
                jogador.x, jogador.y = self.pos_chegada
                self.vencedor = jogador
                return

        if not jogador.movendo and self.valor_dado > 0 and not self.aguardando_turno and not self.quiz_ativo and not self.quiz_aguardando and not self.vencedor:
            # --- So abre quiz se a casa tem pergunta ---
            if jogador.casa_atual in self.casas_com_quiz:
                self.quiz_aguardando = True
                self.quiz_tempo_aguardando = pygame.time.get_ticks()
            else:
                self.aguardando_turno = True
                self.tempo_fim_movimento = pygame.time.get_ticks()

        # --- Espera o delay antes de passar o turno ---
        if self.aguardando_turno:
            if pygame.time.get_ticks() - self.tempo_fim_movimento >= DELAY_ENTRE_TURNOS_MS:
                if not self.algum_jogador_movendo():
                    self.passar_turno()
                    self.valor_dado = 0
                    self.aguardando_turno = False
                    # --- Verifica derrota no modo solo ---
                    if self.quantidade_jogadores == 1 and self.rodada_atual >= DERROTA_LIMITE_RODADAS and not self.vencedor:
                        self.derrota = True
