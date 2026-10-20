*This project has been created as part of the 42 curriculum by fsayuri-, aschulz-.*

# A-Maze-ing

## Descrição

Gerador de labirintos em Python. O programa lê um arquivo de configuração, gera
um labirinto aleatório (reprodutível por seed), salva o resultado num arquivo
em formato hexadecimal e mostra o labirinto no terminal, com um menu
interativo.

O gerador fica num pacote reutilizável (`mazegen`), que vai ser distribuído
como `.whl` para ser usado em projetos futuros.

## Como rodar

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

Quando o Makefile estiver pronto (#3), os atalhos serão:

| Comando | O que faz |
|---|---|
| `make install` | instala as dependências |
| `make run` | roda o programa com o `config.txt` |
| `make debug` | roda com o `pdb` |
| `make clean` | apaga caches (`__pycache__`, `.mypy_cache`...) |
| `make lint` | `flake8` + `mypy` com as flags do subject |
| `make lint-strict` | `flake8` + `mypy --strict` |

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
Um 500x500 gera em cerca de 1 segundo.

#### Por que escolhemos esse algoritmo

- É o mais simples de implementar e de explicar.
- Gera corredores longos, que ficam bonitos no terminal.
- A ordem em que as paredes são abertas já é a ordem natural para a animação
  (`carve_history`).

### Seed

Todo sorteio vem de um `random.Random(seed)` próprio do `MazeGenerator`,
nunca do módulo `random` global. Mesma seed significa os mesmos sorteios e,
portanto, o mesmo labirinto. Sem `SEED` no config, uma seed é sorteada e fica
em `maze.seed`, para dar para reproduzir o labirinto depois.

## Divisão do trabalho

| Quem | Parte | Issues |
|---|---|---|
| **fsayuri-** | **Core (`mazegen/`)**: estrutura do repo, modelo de paredes, padrão 42, algoritmo de geração + seed, menor caminho, modo Pac-Man e empacotamento
| **aschulz-** | **App (`app/`)**: Makefile, parser do config, arquivo de saída, `a_maze_ing.py`, validador, render no terminal, menu, lint e README/LICENSE
| **As duas** | Interface do `MazeGenerator` (contrato core ↔ app), bateria de testes e lint final

## Parte obrigatória

- [ ] Ler e validar o arquivo de configuração, com mensagens de erro claras
- [ ] Gerar um labirinto aleatório e reprodutível pela seed
- [ ] Paredes coerentes entre vizinhos e bordas externas fechadas
- [ ] Todas as células alcançáveis (exceto as do "42")
- [ ] Nenhuma área aberta maior que 2 células de largura (sem 3x3 aberto)
- [ ] Desenhar um "42" com células totalmente fechadas (com mensagem de erro se não couber)
- [ ] `PERFECT=True`: exatamente um caminho entre entrada e saída
- [ ] `PERFECT=False`: tabuleiro estilo Pac-Man (conectado, com cantos e centro abertos, pelo menos 2 loops e poucos becos sem saída)
- [ ] Arquivo de saída em hexadecimal, com entrada, saída e menor caminho (`N/E/S/W`)
- [ ] Visualização no terminal com paredes, entrada, saída e caminho
- [ ] Menu: gerar outro labirinto, mostrar/esconder o caminho, mudar a cor das paredes
- [ ] Pacote `mazegen-*.whl` na raiz e `LICENSE.md`
- [ ] `flake8` e `mypy` sem erros

---

## Bônus (opcional)

> Esta seção é independente da parte obrigatória. S

| Bônus | Descrição | Quem |
|---|---|---|
| Zero dead-ends | modo Pac-Man sem nenhum beco sem saída | fsayuri- |
| Mais algoritmos | escolher o algoritmo de geração (backtracker, Prim, Kruskal) | aschulz- |
| Animação | animar a construção do labirinto **e** a busca do caminho | aschulz- |
