# Monograph Outline — TCC

**Topic**: Time Allocation Strategies for MCTS in Gomoku  
**Writing order**: 2 → 3 → 4 → 5 → 1 → 6

---

## 2. Fundamentação Teórica

### 2.1 Minimax e Busca em Jogos

#### 2.1.1 O algoritmo Minimax

- Modelo de jogo de soma zero entre dois agentes: MAX e MIN
- Busca exaustiva em profundidade na árvore de jogo; retorna movimento ótimo assumindo adversário perfeito
- Complexidade exponencial: inviável sem poda para jogos com alto fator de ramificação

#### 2.1.2 Poda Alfa-Beta

- Elimina ramos que não podem influenciar a decisão — sem alterar o resultado
- Reduz complexidade de `O(b^d)` para `O(b^(d/2))` no melhor caso
- Ainda depende de uma função de avaliação heurística para profundidade limitada

#### 2.1.3 Limitações do Minimax em jogos complexos

- Função de avaliação difícil de definir para jogos como Gomoku e Go
- Profundidade de busca limitada pelo tempo disponível — sensível à qualidade da heurística
- Motivação para abordagens baseadas em simulação (MCTS)

### 2.2 Monte Carlo Tree Search

#### 2.2.1 Visão geral do MCTS

- As quatro fases: Selection, Expansion, Simulation, Backpropagation
- Como o algoritmo constrói a árvore iterativamente sem função de avaliação explícita

#### 2.2.2 UCB1 e o dilema exploração-exploração

- Fórmula UCB1, constante `sqrt(2)`, intuição por trás do balanço

#### 2.2.3 MCTS como algoritmo anytime

- A propriedade central: pode ser interrompido a qualquer momento com resultado válido
- Por que o tempo é o recurso natural de controle (e não o número de iterações)
- Contraste com Minimax: qualidade cresce continuamente com o tempo, sem cliff de profundidade

### 2.3 Gerenciamento de Tempo em Jogos

#### 2.3.1 Controle de tempo em competições (contexto histórico)

- Sistemas de tempo em xadrez e Go (tempo fixo por partida, Fischer, bônus por lance)
- Como os jogadores humanos distribuem o tempo (mais nos momentos críticos)

#### 2.3.2 Tipos de estratégias de alocação de tempo

- **Uniforme (flat)**: divide o tempo restante igualmente entre os movimentos estimados restantes; simples e previsível
- **Proporcional**: variante do flat que se auto-corrige ao longo da partida conforme o tempo real consumido
- **Baseada em fase**: aplica multiplicadores distintos por fase do jogo (abertura, meio, fim), refletindo que nem todas as fases têm a mesma densidade de decisão
- **Reativa (baseada em criticidade)**: detecta posições táticas especiais e aloca mais tempo nelas; requer um critério de detecção de criticidade
- **Adaptativa/aprendida**: ajusta a alocação com base em dados de partidas anteriores (aprendizado por reforço, estatísticas históricas) — fora do escopo deste trabalho, mas mencionada como direção futura

#### 2.3.3 Time management para MCTS — estado da arte

- Referência direta: *Time Management for Monte-Carlo Tree Search Applied to Go* (docs/)
- Referência complementar: *Monte Carlo Algorithms for Time-Constrained General Game Playing* (docs/)
- As estratégias implementadas neste trabalho (Cap. 3) são instâncias dos tipos acima

### 2.4 O Jogo Gomoku

#### 2.4.1 Regras e estrutura

- Tabuleiro 15×15, cinco peças em linha, dois jogadores
- Ausência de empates na prática; assimetria do primeiro movimento (preto)

#### 2.4.2 Características relevantes para o MCTS

- Alto fator de ramificação no início (~225) que decresce ao longo da partida
- Fases distintas (abertura, meio, fim) com diferentes densidades de decisão
- Padrões táticos críticos: 4-em-linha aberta como ameaça imediata de vitória

---

## 3. Proposta

### 3.1 Definição Formal do Problema

- Dado budget total `T` e partida com até `N` movimentos, determinar `t_i` por lance
- Constraint: `sum(t_i) <= T`, com `t_i >= t_min`
- Objetivo: maximizar taxa de vitórias em duelos de longa duração

### 3.2 Arquitetura da Solução

- Diagrama de camadas: `GameState → TimeManager.allocate() → MCTS(time_limit) → move`
- Interface `BaseTimeManager` e sua extensibilidade
- Separação de responsabilidades entre time manager e MCTS

### 3.3 Estratégias Propostas

#### 3.3.1 Flat (Baseline)

- `t = T_restante / N_estimado_restante`
- Por que serve como baseline: simples, justo, previsível
- Parâmetro: 100 movimentos estimados por jogador por partida

#### 3.3.2 Proporcional

- Mesma ideia do flat, mas se auto-corrige conforme a partida avança
- Discussão da diferença sutil em relação ao flat com N = 100

#### 3.3.3 Por Fase (Phase)

- Definição das fases baseada no número de peças no tabuleiro
- Multiplicadores: Abertura 0.6×, Meio do jogo 1.4×, Final 0.8× sobre a alocação flat
- Justificativa: o meio do jogo concentra as decisões táticas mais densas

#### 3.3.4 Crítica (Critical)

- Detecção de ameaças de 4-em-linha para qualquer jogador
- Multiplica por 2.0× quando há ameaça detectada, 0.9× caso contrário
- Justificativa: erros em posições táticas críticas são imediatamente fatais

---

## 4. Implementação

### 4.1 Visão Geral do Sistema

- Diagrama de módulos: `src/game/`, `src/agents/mcts/`, `src/time_manager/`, `run_duel.py`

### 4.2 Motor de Jogo (Gomoku)

- `Board`: representação, `legal_moves()`, detecção de vitória
- `GameState`: `next_state()`, `is_terminal()`, `winner()`

### 4.3 Agente MCTS

#### 4.3.1 Loop principal baseado em tempo

- `while time.time() < deadline` — como o deadline é recebido do time manager
- Número de iterações realizadas como variável observada (não controlada)

#### 4.3.2 Rollout com viés de localidade

- Prioriza movimentos dentro de raio 2 da última peça jogada
- Por que isso acelera convergência no Gomoku (reduz espaço de busca efetivo)

### 4.4 Camada de Gerenciamento de Tempo

- Interface: `allocate(time_remaining, move_number, board, player) -> float`
- Clamp aplicado em todas as estratégias: `[0.05s, time_remaining * 0.95]`
- Implementação de cada estratégia com foco nos pontos de diferenciação

### 4.5 Runner de Torneio (`run_duel.py`)

- Protocolo de duelo: N partidas com alternância de cores
- Coleta de métricas por lance: `time_allocated`, `time_spent`, `time_remaining`
- Formato de saída JSON: `config` + `summary` (por cor) + `matches` (detalhamento completo)
- Reprodutibilidade: todos os parâmetros registrados no campo `config`

---

## 5. Resultados e Análise

### 5.1 Metodologia Experimental

- 100 partidas por par de estratégias, budget de 60s por jogador por partida
- Alternância de cores para controlar o viés do primeiro movimento
- Métricas coletadas: taxa de vitórias geral, taxa por cor (B/W), tempo médio alocado por fase

### 5.2 Resultados por Estratégia

#### 5.2.1 Flat vs Flat (self-play — sanity check)

- Resultado esperado: ~50/50; confirma ausência de viés na infraestrutura
- Reportar viés de cor observado (B tende a vencer mais)

#### 5.2.2 Proporcional vs Flat

- Win rate + intervalo de confiança binomial (95%)
- Discussão: proporcional e flat convergem quando N = 100 e o orçamento não é esgotado

#### 5.2.3 Phase vs Flat

- Win rate + intervalo de confiança
- Análise: bônus no meio do jogo se traduz em vitórias? Em que condições?

#### 5.2.4 Critical vs Flat

- Win rate + intervalo de confiança
- Análise: detecção de ameaças táticas traz ganho mensurável?

### 5.3 Análise Temporal

- Distribuição do tempo alocado ao longo da partida por estratégia (gráfico)
- Diferença entre `time_allocated` e `time_spent` — overhead do MCTS
- Iterações MCTS realizadas por fase do jogo como proxy de profundidade de busca

### 5.4 Discussão

- O viés do primeiro movimento (jogador preto) e como ele pode dominar o sinal
- Nota sobre intervalos de confiança: com 100 partidas, um resultado 55/100 tem IC ~[0.45, 0.65] — discutir significância
- Limitações: budget fixo, apenas Gomoku, rollout não treinado
- O que phase e critical ganham (ou não) e hipóteses explicativas

---

## 1. Introdução

### 1.1 Contextualização

- Jogos de tabuleiro como ambiente clássico de pesquisa em IA
- MCTS e seu papel central em agentes modernos (referência ao AlphaGo/AlphaZero)
- O problema de gerenciamento de recursos computacionais em tempo real

### 1.2 Motivação

- MCTS é anytime: mais tempo = melhor qualidade, mas o budget por partida é fixo
- A questão: *como distribuir o tempo fixo entre os movimentos de forma ótima?*
- Estratégias ingênuas ignoram que alguns momentos do jogo são mais críticos que outros

### 1.3 Objetivos

**Geral**: Comparar estratégias de alocação de tempo por lance em agentes MCTS no Gomoku e medir o impacto na taxa de vitórias.

**Específicos**:

- Implementar variantes de alocação (flat, proporcional, por fase, crítica)
- Desenvolver infraestrutura de torneio para coleta de dados controlada
- Medir o impacto de cada estratégia via duelos com condições controladas
- Analisar trade-offs e limitações de cada abordagem

### 1.4 Hipótese

- Alocação inteligente (phase/critical) supera a baseline flat em taxa de vitórias

### 1.5 Organização do Trabalho

- Breve descrição dos capítulos (escrever por último, após tudo pronto)

---

## 6. Conclusão

### 6.1 Síntese dos Resultados

- Qual estratégia obteve melhor desempenho e com qual magnitude

### 6.2 Resposta à Hipótese

- A hipótese foi confirmada, refutada ou inconclusiva? Com que grau de confiança?

### 6.3 Contribuições

- Infraestrutura de torneio reusável para comparar agentes MCTS
- Framework extensível de time managers via `BaseTimeManager`
- Dados empíricos sobre o impacto de time management no Gomoku

### 6.4 Limitações

- Rollout não treinado (random com viés local) — MCTS mais forte poderia reagir diferente
- Apenas Gomoku — generalização não testada
- Detecção de criticidade limitada a 4-em-linha (padrões sutis ignorados)

### 6.5 Trabalhos Futuros

- Neural network policy para rollout (estilo AlphaZero)
- Detecção de criticidade mais sofisticada (VCT, padrões 3×3)
- Generalização para outros jogos (Othello, Go)
- Adaptive time manager que aprende a distribuição ótima via self-play

---

## Referências Chave

| Arquivo em `docs/` | Usar em |
| --- | --- |
| `MCTS-survey.pdf` (Browne et al.) | Cap. 2.1 — base do MCTS |
| `Time_Management_for_Monte-Carlo_Tree_Search_Applied_to_the_Game_of_Go.pdf` | Cap. 2.2 e validação do design no Cap. 3 |
| `Monte_Carlo_Algorithms_for_Time-Constrained_General_Game_Playing.pdf` | Cap. 2.2 e suporte ao Cap. 3 |
| `time_management_for_monte_carlo_tree_search.pdf` | Cap. 2.2 — complementar |

---

## Notas para a Escrita

- **Intervalos de confiança**: calcule antes de escrever o Cap. 5. Com 100 partidas, um resultado 55/100 tem IC 95% de ~[0.45, 0.65] — o efeito precisa ser maior que a margem para ser conclusivo.
- **Seção 1.5** (Organização do Trabalho): escrever por último, após todos os outros capítulos estarem prontos.
- **Figuras sugeridas**: diagrama de arquitetura (Cap. 3/4), gráfico de distribuição de tempo por fase (Cap. 5.3), tabela de win rates com IC (Cap. 5.2).
