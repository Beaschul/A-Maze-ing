*This project has been created as part of the 42 curriculum by fsayuri-, aschulz-.*

# A-Maze-ing

## Descrição

Gerador de labirintos em Python. O programa lê um arquivo de configuração, gera
um labirinto aleatório (reprodutível por seed), salva o resultado num arquivo
em formato hexadecimal e mostra o labirinto no terminal, com um menu
interativo.

O gerador fica num pacote reutilizável (`mazegen`), que vai ser distribuído
como `.whl` para ser usado em projetos futuros.

## Instruções

Requisito: Python 3.10 ou mais novo.

```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar as ferramentas de desenvolvimento (flake8, mypy, pytest, build)
pip install -r requirements.txt

# 3. Rodar o programa
python3 a_maze_ing.py config.txt

# 4. Rodar os testes
python3 -m pytest
```

Ou, com o Makefile (não precisa ativar a venv):

```bash
make install
make run
```

| Comando | O que faz |
|---|---|
| `make install` | cria a `.venv` e instala as dependências do `requirements.txt` |
| `make run` | roda `a_maze_ing.py` com o `config.txt` |
| `make debug` | roda com o `pdb` |
| `make clean` | apaga caches (`__pycache__`, `.mypy_cache`...) e artefatos de build |
| `make fclean` | `make clean` e apaga a `.venv` |
| `make lint` | `flake8` + `mypy` com as flags do subject |
| `make lint-strict` | `flake8` + `mypy --strict` |
| `make test` | roda os testes com `pytest` |
| `make test-analyzer` | roda o `maze_analyzer` em todos os configs de teste, 50 seeds cada |
| `make check` | `make test` + `make test-analyzer`: mostra tudo o que falhou |
| `make build` | gera o pacote `mazegen` (`.whl` e `.tar.gz`) |

`lint`, `lint-strict`, `test`, `test-analyzer` e `build` instalam as
dependências sozinhos se a `.venv` ainda não tiver elas (ou se o
`requirements.txt` mudar). Para usar outro arquivo de configuração:
`make run CONFIG=outro.txt`.

### Build do pacote `mazegen`

```bash
make build    # gera mazegen-1.0.0-py3-none-any.whl e mazegen-1.0.0.tar.gz na raiz
pip install mazegen-1.0.0-py3-none-any.whl
```

O `.whl` e o `.tar.gz` já ficam versionados na raiz do repositório. Só o
pacote `mazegen/` entra neles: `app/`, `tests/` e `tools/` ficam de fora.

### Bateria do analyzer

`tools/run_analyzer.py` gera um labirinto para cada arquivo de
`tests/configs_valid/` e cada seed (trocando `SEED` e `OUTPUT_FILE`) e confere:

- o veredito do `tools/maze_analyzer.py`: `PERFECT maze` com `PERFECT=True`
  (paredes coerentes, tudo conectado, nenhum ciclo) e `Pac-Man-USABLE` com
  `PERFECT=False` (pelo menos 2 rotas independentes, no máximo 2 dead-ends
  reais, cantos e centro alcançáveis);
- o caminho do rodapé: sai da entrada, não atravessa parede, chega na saída e
  é o mais curto;
- o "42": desenhado quando cabe (9x7 ou maior), ausente quando não cabe.

Um config que começa com `# EXPECT_ERROR: <texto>` precisa ser recusado com
uma mensagem que contenha `<texto>`. Para rodar só alguns configs:
`python3 tools/run_analyzer.py --seeds 5 tests/configs_valid/3x3_perfect.txt`.

### Arquivo de configuração

Uma chave `KEY=VALUE` por linha. As linhas que começam com `#` são ignoradas.

| Chave | Obrigatória | Descrição | Exemplo |
|---|---|---|---|
| `WIDTH` | sim | largura em células | `WIDTH=20` |
| `HEIGHT` | sim | altura em células | `HEIGHT=15` |
| `ENTRY` | sim | célula de entrada `x,y` | `ENTRY=0,0` |
| `EXIT` | sim | célula de saída `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | sim | arquivo de saída | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | sim | labirinto perfeito? | `PERFECT=True` |
| `SEED` | não | mesma seed = mesmo labirinto | `SEED=42` |

Regras de leitura:

- As chaves aceitam maiúsculas ou minúsculas: `width=20` vale como
  `WIDTH=20` (e as duas juntas contam como chave repetida).
- Espaços em volta do `=` e no começo/fim da linha são ignorados
  (`WIDTH = 20` funciona).
- A linha é separada no primeiro `=`; linha sem `=` é erro.
- Chave repetida é erro. Chave desconhecida só gera um aviso e é ignorada.
- `WIDTH` e `HEIGHT` são inteiros entre 2 e 500.
- `ENTRY` e `EXIT` ficam dentro do grid e são células diferentes.
- `PERFECT` aceita `True` ou `False`, em maiúsculas ou minúsculas.
- `OUTPUT_FILE` não pode ser vazio nem ser o próprio arquivo de configuração.
- Arquivos salvos com BOM (comum no Windows) são aceitos.

Qualquer erro mostra uma mensagem `ConfigError: ...`, com o número da linha
quando ele existe, e o programa sai com código 1. Há um exemplo de cada erro
em [`tests/configs_invalid/`](tests/configs_invalid/), testados em
`tests/app/test_config.py`.

## Menu interativo

Depois de gerar e salvar o labirinto, o programa desenha o labirinto e mostra
um menu (`app/menu.py`). O ciclo é: desenhar → mostrar o menu → ler a opção →
agir.

```
Seed: 42  |  20x15  |  perfect  |  shortest path: 89 steps  |  file: maze.txt
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show/Hide the shortest path
3. Change wall colours
4. Quit
Your choice:
```

| Opção | O que faz |
|---|---|
| `1` | Gera um labirinto novo com uma **seed aleatória nova** e **reescreve o `OUTPUT_FILE`**, para o arquivo sempre bater com o que está na tela. A seed nova aparece na linha de status, então o labirinto pode ser reproduzido com `SEED=<seed>`. |
| `2` | Mostra/esconde o menor caminho. |
| `3` | Troca a paleta: cor das paredes e cor própria do "42". |
| `4` | Sai do programa. |

- Mostrar/esconder o caminho e a paleta continuam valendo depois de regenerar.
- Entrada inválida (vazia, letras, número fora do menu) só mostra uma mensagem
  e pergunta de novo.
- `Ctrl+D` (`EOFError`) e `Ctrl+C` (`KeyboardInterrupt`) saem do menu como a
  opção 4, sem traceback.
- Se não der para salvar o labirinto novo (ex.: permissão), aparece um
  `WriteError` e o programa continua rodando.

## Algoritmo de geração

### O que é um labirinto perfeito

Pense em cada célula como um ponto e em cada parede aberta como uma ligação
entre dois pontos. Um labirinto é **perfeito** quando existe **exatamente um
caminho** entre quaisquer duas células. Isso é o mesmo que dizer que as
ligações formam uma **árvore**:

- tudo está conectado (dá para chegar em qualquer célula);
- não há nenhum ciclo (não dá para andar em círculo e voltar ao mesmo lugar).

Uma árvore com `N` células tem sempre `N - 1` ligações. Então, num labirinto
perfeito, o número de paredes abertas é o número de células livres menos 1
(os testes verificam exatamente isso).

### Recursive backtracker (busca em profundidade)

É o algoritmo usado (`mazegen/algorithms/backtracker.py`). A ideia é a de
alguém andando num labirinto com um rolo de barbante:

1. Começa com **todas as paredes fechadas** e fica na célula de entrada.
2. Olha os vizinhos da célula atual que **ainda não foram visitados**.
3. Se houver algum, **sorteia um**, abre a parede entre os dois e anda para
   ele (o barbante vai junto).
4. Se não houver nenhum (beco sem saída), **volta uma célula** seguindo o
   barbante e tenta de novo a partir dali.
5. Termina quando voltou até o início e não sobrou nenhum vizinho novo.

O "barbante" é uma **pilha**: andar para frente empilha a célula, voltar
desempilha.

#### Exemplo num labirinto 3x2

Numerando as células na ordem em que são visitadas (os sorteios são só um
exemplo):

| Passo | Célula atual | Vizinhos não visitados | O que acontece | Pilha |
|---|---|---|---|---|
| 1 | `1` (0,0) | (1,0), (0,1) | sorteia (1,0), abre a parede | `1 2` |
| 2 | `2` (1,0) | (2,0), (1,1) | sorteia (1,1), abre a parede | `1 2 3` |
| 3 | `3` (1,1) | (0,1), (2,1) | sorteia (0,1), abre a parede | `1 2 3 4` |
| 4 | `4` (0,1) | nenhum | beco sem saída: volta | `1 2 3` |
| 5 | `3` (1,1) | (2,1) | abre a parede | `1 2 3 5` |
| 6 | `5` (2,1) | (2,0) | abre a parede | `1 2 3 5 6` |
| 7 | `6` (2,0) | nenhum | volta... até a pilha esvaziar | vazia |

Resultado: 6 células e 5 paredes abertas (6 - 1), ou seja, uma árvore.

```
+---+---+---+
| 1   2 | 6 |
+---+   +   +
| 4   3   5 |
+---+---+---+
```

#### Por que sempre dá um labirinto perfeito

- **Sem ciclos:** só abre parede para uma célula **não visitada**. Nunca liga
  duas células que já tinham um caminho entre si.
- **Tudo conectado:** uma célula só sai da pilha depois que todos os vizinhos
  dela foram visitados. Quando a pilha esvazia, não sobrou nenhuma célula
  alcançável sem visitar.
- **Regra do 3x3:** uma árvore nunca tem um bloco 2x2 aberto (ele seria um
  ciclo), então nunca aparece uma área aberta 3x3.

#### Por que pilha e não recursão

A versão "de livro" é recursiva, mas o Python para com erro depois de cerca
de 1000 chamadas aninhadas. Num labirinto grande o caminho chega a milhares
de células, então a pilha é uma lista comum (`stack.append` / `stack.pop`).
Um 500x500 perfeito gera em cerca de 2 segundos.

#### Por que escolhemos esse algoritmo

- É o mais simples de implementar e de explicar.
- Gera corredores longos, que ficam bonitos no terminal.
- A ordem em que as paredes são abertas fica gravada em `carve_history`:
  dados prontos para uma animação futura (a animação não foi implementada).

### Modo Pac-Man (`PERFECT=False`)

Parte do labirinto perfeito do backtracker e faz um *braid*
(`mazegen/braid.py`): visita os becos sem saída e abre mais uma parede em
cada um, o que transforma o beco em corredor e cria um ciclo. Para cada
parede que abre:

- nunca abre a borda externa nem uma célula do "42";
- nunca cria uma área 3x3 aberta (`creates_open_area`, em
  `mazegen/validator.py`);
- prefere não criar salas 2x2, para os corredores ficarem finos, e prefere
  abrir na direção de outro beco, resolvendo os dois de uma vez.

No fim, se o labirinto tiver menos de 2 ciclos independentes (`MIN_LOOPS`,
em `mazegen/constants.py`), abre paredes extras. Um 2x2 não comporta isso e
dá erro `MazeError` com mensagem clara.

**Bônus (sem becos):** na prática, o tabuleiro sai sem nenhum beco sem saída
real. Para conferir:
`python3 tools/maze_analyzer.py maze.txt --max-dead-ends 0`.

### Seed

Todo sorteio vem de um `random.Random(seed)` próprio do `MazeGenerator`,
nunca do módulo `random` global. Mesma seed significa os mesmos sorteios e,
portanto, o mesmo labirinto. Sem `SEED` no config, uma seed é sorteada e fica
em `maze.seed`, para dar para reproduzir o labirinto depois.

## Menor caminho

### Busca em largura (BFS)

Para achar o menor caminho da entrada até a saída usamos uma **busca em
largura** (BFS, *breadth-first search*). A ideia é a de uma gota de tinta
caindo na entrada e se espalhando pelos corredores:

1. Primeiro a tinta chega em todas as células a **1 passo** da entrada.
2. Depois em todas a **2 passos**, depois a **3**, e assim por diante.
3. A primeira vez que a tinta encosta na saída, ela chegou pelo caminho mais
   curto, porque todas as células mais perto já tinham sido pintadas antes.

Isso funciona porque todo passo custa o mesmo (uma célula). No modo perfeito
só existe um caminho, então o BFS acha esse. No modo Pac-Man existem vários,
e o BFS acha um dos mais curtos.

### Fila (`collections.deque`)

O que faz a tinta se espalhar "em camadas" é usar uma **fila**: quem entra
primeiro sai primeiro, como fila de banco.

- `fila.append(celula)`: coloca no **fim** da fila.
- `fila.popleft()`: tira do **começo** da fila.

Compare com o backtracker, que usa uma **pilha** (tira do fim, o último que
entrou). Trocar pilha por fila é exatamente o que muda o algoritmo de "ir o
mais fundo possível" para "ir camada por camada".

Por que `deque` e não uma lista? Numa lista, `lista.pop(0)` precisa empurrar
todos os outros elementos uma posição para a esquerda, então fica lento numa
fila grande. O `deque` (*double-ended queue*) tira do começo sem mexer no
resto, sempre na mesma velocidade.

```python
from collections import deque

fila = deque([(0, 0)])
fila.append((1, 0))   # fila: (0,0) (1,0)
fila.popleft()        # devolve (0,0); fila: (1,0)
```

### Reconstruindo o caminho

O BFS não lembra o caminho inteiro de cada célula, só **de onde veio**: ao
descobrir uma célula nova, guardamos o "pai" dela (a célula de onde chegamos)
e a direção do passo. Quando chega na saída, é só ir seguindo os pais de trás
para frente até a entrada e inverter a lista.

### Exemplo no labirinto 3x2

Usando o labirinto do exemplo acima, com entrada `A = (0,0)` e saída
`B = (2,0)`:

```
+---+---+---+
| A     | B |
+---+   +   +
|           |
+---+---+---+
```

| Passo | Tira da fila | Vizinhos novos (parede aberta) | Fila depois |
|---|---|---|---|
| 1 | (0,0) | (1,0) pai (0,0) via E | (1,0) |
| 2 | (1,0) | (1,1) pai (1,0) via S | (1,1) |
| 3 | (1,1) | (2,1) via E, (0,1) via W | (2,1) (0,1) |
| 4 | (2,1) | (2,0) via N | (0,1) (2,0) |
| 5 | (0,1) | nenhum | (2,0) |
| 6 | (2,0) | é a saída: para | |

Seguindo os pais a partir da saída: `(2,0) ←N (2,1) ←E (1,1) ←S (1,0) ←E
(0,0)`. Invertendo: **`ESEN`**.

A ordem da coluna "Tira da fila" é o `search_history`, guardado para uma
animação futura da busca.

## Parte reutilizável: o pacote `mazegen`

Tudo o que gera e resolve o labirinto fica em `mazegen/`, sem depender do
`app/`: o pacote não imprime nada, não lê entrada e não chama `exit()`. Todo
problema vira uma `MazeError`. Só usa a biblioteca padrão e é totalmente
tipado (`py.typed`).

### Instanciar e passar parâmetros

```python
from mazegen import Direction, MazeError, MazeGenerator

maze = MazeGenerator(
    20, 15,                # largura e altura (2 a 500)
    entry=(0, 0),          # (x, y): x = coluna, y = linha
    exit=(19, 14),
    perfect=True,          # False = tabuleiro Pac-Man
    seed=42,               # opcional: sem seed, uma é sorteada
)
maze.generate()
```

### Acessar a estrutura e a solução

```python
maze.seed                                # 42 (ou a seed sorteada)
maze.grid                                # grid[y][x]: máscara de 4 bits por célula
maze.has_wall((0, 0), Direction.NORTH)   # True
maze.pattern_cells                       # células do "42" (sempre fechadas)
maze.solution                            # [(0, 0), (1, 0), ...] da entrada à saída
maze.solution_directions                 # "EESEN..."
maze.carve_history                       # paredes abertas, em ordem (para animação futura)
maze.search_history                      # células visitadas pelo BFS, em ordem (idem)

try:
    MazeGenerator(20, 15, entry=(0, 0), exit=(20, 0))
except MazeError as err:
    print(err)  # exit (20, 0) is outside the 20x15 maze
```

Bits das paredes: `NORTH = 1`, `EAST = 2`, `SOUTH = 4`, `WEST = 8`; bit ligado
= parede fechada. Uma instância = um labirinto: para outro labirinto, crie
outro `MazeGenerator`. Mais detalhes (e como escrever o arquivo de saída) em
[`mazegen/README.md`](mazegen/README.md).

## Equipe e gestão do projeto

| Quem | Parte |
|---|---|
| **fsayuri-** | **Core (`mazegen/`)**: estrutura do repo, interface pública, modelo de paredes, padrão 42, algoritmo de geração + seed, menor caminho, modo Pac-Man, validador interno e empacotamento |
| **aschulz-** | **App (`app/`)**: Makefile, parser do config, arquivo de saída, `a_maze_ing.py`, bateria do analyzer, render no terminal, menu, lint e README/LICENSE |
| **As duas** | Interface do `MazeGenerator` (contrato core ↔ app), revisão dos PRs e testes |

### Planejamento e evolução

Em 14/10 quebramos o subject em 21 issues no GitHub (core, app, infra e
bônus). O core ficou pronto até 22/10 e o app e o empacotamento até 31/10.

### O que funcionou e o que melhorar

Funcionou definir cedo o contrato do `MazeGenerator` (issue #2): core e app
andaram em paralelo. A melhorar: os bônus de animação e de um segundo
algoritmo de geração ficaram para uma próxima versão.

## Ferramentas

- **Python 3.10+**, só com a biblioteca padrão no código do projeto.
- **venv** + **Makefile** para instalar, rodar, testar e gerar o pacote.
- **flake8** e **mypy** (flags do subject e `--strict`).
- **pytest** para os testes e `tools/maze_analyzer.py` /
  `tools/run_analyzer.py` para validar labirintos gerados.
- **build** + **setuptools** para gerar o `.whl` e o `.tar.gz`.
- **Git** e **GitHub** (issues, milestones e pull requests).
- **VS Code** com **Claude Code** (ver Recursos).

## Recursos

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm):
  recursive backtracker, Prim, Kruskal.
- [Think Labyrinth! (Walter D. Pullen)](https://www.astrolog.org/labyrnth/algrithm.htm):
  classificação de labirintos, labirintos perfeitos e *braid* (sem becos).
- Jamis Buck, [Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
  e o livro *Mazes for Programmers*.
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search).
- Documentação do Python: [`random`](https://docs.python.org/3/library/random.html),
  [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque),
  [`typing`](https://docs.python.org/3/library/typing.html).
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
  para o `pyproject.toml` e o build do pacote.
- [choosealicense.com](https://choosealicense.com/) para escolher a licença.

### Uso de IA

Usamos o **Claude Code** (Anthropic) como assistente durante o projeto:

- **Planejamento:** ajudar a quebrar o subject em milestones e issues.
- **Explicação de conceitos:** labirinto perfeito como árvore, backtracker
  com pilha x recursão, BFS com `deque`, *braid*.
- **Testes:** sugerir casos de borda para o parser do config (os arquivos de
  `tests/configs_invalid/`) e para o gerador.
- **Revisão e lint:** encontrar erros de `flake8` / `mypy` e revisar PRs.
- **Documentação:** rascunho de docstrings, deste README e do `LICENSE.md`.

Todo código sugerido foi lido, entendido e testado por nós antes de entrar
no repositório; as decisões de design (contrato do `MazeGenerator`,
algoritmo, formato do config) foram nossas.

## Parte obrigatória

- [x] Ler e validar o arquivo de configuração, com mensagens de erro claras
- [x] Gerar um labirinto aleatório e reprodutível pela seed
- [x] Paredes coerentes entre vizinhos e bordas externas fechadas
- [x] Todas as células alcançáveis (exceto as do "42")
- [x] Nenhuma área aberta maior que 2 células de largura (sem 3x3 aberto)
- [x] Desenhar um "42" com células totalmente fechadas (com mensagem de erro se não couber)
- [x] `PERFECT=True`: exatamente um caminho entre entrada e saída
- [x] `PERFECT=False`: tabuleiro estilo Pac-Man (conectado, com cantos e centro abertos, pelo menos 2 loops e poucos becos sem saída)
- [x] Arquivo de saída em hexadecimal, com entrada, saída e menor caminho (`N/E/S/W`)
- [x] Visualização no terminal com paredes, entrada, saída e caminho
- [x] Menu: gerar outro labirinto, mostrar/esconder o caminho, mudar a cor das paredes
- [x] Pacote `mazegen-*.whl` na raiz e `LICENSE.md`
- [x] `flake8` e `mypy` sem erros

## Licença

[MIT](LICENSE.md). Escolhemos uma licença **permissiva** porque o `mazegen`
foi feito para ser reutilizado: qualquer pessoa pode usar, modificar e
redistribuir o código (inclusive em projetos fechados), desde que mantenha o
aviso de copyright. Uma licença **copyleft** como a GPL obrigaria quem
distribui uma versão modificada a liberar o código sob a mesma licença, o
que restringe o reuso; para uma biblioteca pequena de estudo, não fazia
sentido.
