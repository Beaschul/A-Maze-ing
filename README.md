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
| Mais algoritmos | escolher o algoritmo de geração (backtracker, Prim, Kruskal) pela chave `ALGORITHM` | aschulz- |
| Animação | animar a construção do labirinto **e** a busca do caminho | aschulz- |
