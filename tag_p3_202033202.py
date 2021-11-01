import math
import random

class SudokuBase:
    # Métodos básicos de um Sudoku:
    # Gerar um grafo vazio, preenchê-lo e imprimi-lo
    
    def __init__(self, base_size):
        self.base_size = base_size
        self.base_color = 0
        self.sudoku_graph = dict()
        
    def get_pos(self, e, base):
        # Retorna x, y = linha, coluna de uma célula de índice e (primeira linha vai de 1 a 9, segunda de 10 a 18 etc)
        # Entendendo o Sudoku como uma matriz 9x9
        quot = e//base
        rest = e%base

        if rest != 0:
            x = quot + 1
            y = rest
        else:
            x = quot
            y = base

        return x, y

    def get_blocks_cord(self, blocks_size):
        blocks = []

        # Um bloco é formado a cada n linhas e n colunas na matriz, onde n é a base do Sudoku
        for i in range(1, blocks_size+1):
            sup_lim_i = (blocks_size*i)+1
            inf_lim_i = sup_lim_i - blocks_size

            for j in range(1, blocks_size+1):
                sup_lim_j = (blocks_size*j)+1
                inf_lim_j = sup_lim_j - blocks_size

                blocks.append([list(range(inf_lim_i, sup_lim_i)), list(range(inf_lim_j, sup_lim_j))])

        return blocks

    def get_block(self, p, blocks, base):
        # Identifica em qual bloco uma célula está na matriz do Sudoku pelo seu índice
        p_x, p_y = self.get_pos(p, base)

        block_c = []

        for b in blocks:
            if (p_x in b[0]) and (p_y in b[1]):
                return b

    def same_blocks(self, a, b, blocks, base):
        return self.get_block(a, blocks, base) == self.get_block(b, blocks, base)

    def same_col(self, a, b, base):
        a_x, a_y = self.get_pos(a, base)
        b_x, b_y = self.get_pos(b, base)

        return a_y == b_y

    def same_row(self, a, b, base):
        a_x, a_y = self.get_pos(a, base)
        b_x, b_y = self.get_pos(b, base)

        return a_x == b_x
        
    def get_col_graph(self, graph):
        if "neighbors" in graph[list(graph.keys())[0]]:
            return {n: {"neighbors": graph[n]["neighbors"], "color": self.base_color} for n in graph.keys()}

        return {n: {"neighbors": graph[n], "color": self.base_color} for n in graph.keys()}
    
    def get_sudoku_redux(self, sudoku_graph):
        # Simplifica um grafo Sudoku, deixando apenas rótulo e cor preenchida
        return {v: sudoku_graph[v]["color"] for v in sudoku_graph.keys()}
        
    def update_col_graph(self):
        # Adiciona a chave "given" para distinguir células dadas de um Sudoku e células que podem ser preenchidas pelo usuário
        self.sudoku_graph = {n: {"neighbors": self.sudoku_graph[n]["neighbors"], "color": self.sudoku_graph[n]["color"], "given": self.sudoku_graph[n]["color"] != self.base_color} for n in self.sudoku_graph.keys()}
        
    def gen_empty_sudoku(self):
        # Gera um grafo Sudoku vazio dentro do próprio objeto da classe
        blocks_size = int(math.sqrt(self.base_size))
        nodes = list(range(1, (self.base_size**2)+1))
        graph = {v: set() for v in nodes}
        bls = self.get_blocks_cord(blocks_size)

        for a in graph.keys():
            for b in graph.keys():
                if (a != b) and (self.same_blocks(a, b, bls, self.base_size) or self.same_col(a, b, self.base_size) or self.same_row(a, b, self.base_size)):
                    graph[a].add(b)

        empty_graph = self.get_col_graph(graph)
        
        self.sudoku_graph = empty_graph
        self.update_col_graph()
        
    def get_empty_sudoku_graph(self):
        # Gera um grafo Sudoku vazio que é retornado como objeto pela função
        blocks_size = int(math.sqrt(self.base_size))
        nodes = list(range(1, (self.base_size**2)+1))
        graph = {v: set() for v in nodes}
        bls = self.get_blocks_cord(blocks_size)

        for a in graph.keys():
            for b in graph.keys():
                if (a != b) and (self.same_blocks(a, b, bls, self.base_size) or self.same_col(a, b, self.base_size) or self.same_row(a, b, self.base_size)):
                    graph[a].add(b)

        return graph
    
    def text_sudoku(self, sudoku_redux):
        text_sudoku = "-"*25 + "\n"

        for i in sudoku_redux.keys():
            lin_i, col_i = self.get_pos(i, 9)

            if col_i == 1:
                text_sudoku += "| "

            text_sudoku += str(sudoku_redux[i])

            # Se for o último elemento da linha, não precisa de espaço, mas de quebramento de linha
            if col_i%9 != 0:
                text_sudoku += " "
            else:
                text_sudoku += " |\n"

            # Imprimir a divisão de blocos nas colunas
            if (col_i%3 == 0) and (col_i != 9):
                text_sudoku += "| "

            # Imprimir a divisão de blocos nas linhas
            if (lin_i%3 == 0) and (col_i%9==0) and (lin_i%9!=0):
                text_sudoku += "-"*25
                text_sudoku += "\n"

        text_sudoku += "-"*25

        return text_sudoku
        
    def print_sudoku(self):
        redux_sudoku_n = self.get_sudoku_redux(self.sudoku_graph)
        text_print = self.text_sudoku(redux_sudoku_n)
        
        print(text_print)

    def fill_cell(self, index, val):
        # Se a célula foi dada, "given", usuário não pode alterá-la
        if self.sudoku_graph[index]["given"]:
            return False

        self.sudoku_graph[index]["color"] = val

        return True

class SudokuAlgorithms(SudokuBase):
    # Métodos com os algoritmos de coloração usados:
    # M coloring com backtracking eficiente (retorna a 1a solução encontrada)
    # E M coloring com backtracking que retorna todas as soluções possíveis
    
    # Códigos e pseudo códigos que serviram de base para o programa:
    # https://www.tutorialspoint.com/M-Coloring-Problem
    # https://www.geeksforgeeks.org/m-coloring-problem-backtracking-5/
    
    def __init__(self, base_size):
        super().__init__(base_size)
        self.solutions = []

    def is_valid_color(self, col_graph, v, col):
        for n in col_graph[v]["neighbors"]:
            if col == col_graph[n]["color"]:
                return False

        return True

    def is_safe_v(self, col_graph, v, c):
        for n in col_graph[v]["neighbors"]:
            if c == col_graph[n]["color"]:
                return False

        return True
        
    def m_coloring_effic(self, col_graph, n, colors):
        # A diferença aqui é que na primeira solução encontrada a recursão é interrompida
        # Busca eficiente de uma solução, sem precisar fazer backtracking para todas cores possíveis
        if n == len(col_graph.keys())+1:
            self.sudoku_graph = col_graph
            return True

        random.shuffle(colors)
        for c in colors:
            if self.is_valid_color(col_graph, n, c):
                col_graph[n]["color"] = c

                if self.m_coloring_effic(col_graph, n+1, colors):
                    return True

                col_graph[n]["color"] = 0

        return False
        
    def erase_random_cell(self):
        cell_erase = random.randint(1, len(self.sudoku_graph.keys()))

        while self.sudoku_graph[cell_erase]["color"] == 0:
            cell_erase = random.randint(1, len(self.sudoku_graph.keys()))

        # Quando uma célula é apagada no grafo, a configuração dele muda, precisando ser atualizada
        self.sudoku_graph[cell_erase]["color"] = 0
        self.update_col_graph()
        self.solutions = []
        
    def graph_coloring_v(self, col_graph, n, colors, print_steps=False):
        # Algoritmo de M coloração por backtracking para achar todas soluções possíveis
        if n == len(col_graph.keys())+1:
            self.solutions.append({v: col_graph[v]["color"] for v in col_graph.keys()})
            
            if (len(self.solutions) == 1) and print_steps:
                # Passo-a-passo é exibido para Sudoku dado (logo, só tem 1 solução)
                print("Solução encontrada.")

            return

        if not col_graph[n]["given"]:
            if (len(self.solutions) == 0) and print_steps:
                print("Mapeando cores possíveis para " + str(n))
            
            for c in colors:
                # Se nó aceita uma cor disponível, segue com ela e passa para o próximo nó
                if self.is_safe_v(col_graph, n, c):
                    
                    if (len(self.solutions) == 0) and print_steps:
                        print("Cor " + str(c) + " é possível para " + str(n))
                        
                    col_graph[n]["color"] = c

                    if (len(self.solutions) == 0) and print_steps:
                        print("Partindo para o próximo vértice:")
                        
                    self.graph_coloring_v(col_graph, n+1, colors, print_steps)

                    # Na volta da recursão, apaga a cor para testar uma cor diferente e achar todas as combinações possíveis
                    col_graph[n]["color"] = 0
                else:
                    if (len(self.solutions) == 0) and print_steps:
                        print("Cor " + str(c) + " não é possível para " + str(n) + ". Partindo para a próxima cor.")
        else:
            self.graph_coloring_v(col_graph, n+1, colors, print_steps)

class SudokuSolver(SudokuAlgorithms):
    # Métodos que usam os algoritmos do Sudoku para gerar Sudoku, gerar solução e resolver um Sudoku preenchido
    
    def __init__(self, base_size):
        super().__init__(base_size)
        
    def gen_random_solution(self):
        empty_graph = self.get_empty_sudoku_graph()
        colored_empty_graph = self.get_col_graph(self.sudoku_graph)
        
        available_colors = list(range(1, self.base_size+1))
        self.m_coloring_effic(colored_empty_graph, 1, available_colors)
        self.update_col_graph()
        
    def gen_random_sudoku(self):
        # Gera um Sudoku completo aleatoriamente
        # Depois, apaga o máximo de células possíveis sem que o Sudoku tenha mais de apenas uma solução
        available_colors = list(range(1, self.base_size+1))
        self.gen_random_solution()
        
        self.erase_random_cell()
        self.graph_coloring_v(self.sudoku_graph, 1, available_colors)
        
        while len(self.solutions) == 1:
            last_graph = {v: self.sudoku_graph[v]["color"] for v in self.sudoku_graph.keys()}
            self.erase_random_cell()
            self.graph_coloring_v(self.sudoku_graph, 1, available_colors)

        for i in last_graph.keys():
            self.sudoku_graph[i]["color"] = last_graph[i]
        
        self.update_col_graph()
        self.solutions = []
        
    def solve_sudoku(self, print_steps=False):
        # Resolve Sudoku pela função que entrega todas as combinações possíveis
        available_colors = list(range(1, self.base_size+1))
        self.graph_coloring_v(self.sudoku_graph, 1, available_colors, print_steps)
        
        n_solution = self.solutions[0]
        for i in n_solution.keys():
            self.sudoku_graph[i]["color"] = n_solution[i]
    
        self.solutions = []
        
        self.update_col_graph()

class SudokuUser(SudokuSolver):
    # Métodos exclusivos de interação com usuário no programa
    
    def __init__(self, base_size):
        super().__init__(base_size)
        
    def fill_given_sudoku(self, given_sudoku):
        self.gen_empty_sudoku()

        for i in given_sudoku.keys():
            self.sudoku_graph[i]["color"] = given_sudoku[i]

        self.update_col_graph()
        
    def solution_checker(self):
        for v in self.sudoku_graph.keys():
            for n in self.sudoku_graph[v]["neighbors"]:
                if (self.sudoku_graph[v]["color"] == 0) or (self.sudoku_graph[v]["color"] == self.sudoku_graph[n]["color"]):
                    return False

class UserInterface:
    # Interface via terminal com usuário
    
    def __init__(self):
        self.user_on = True
        
    def get_pos(self, e, base):
        quot = e//base
        rest = e%base

        if rest != 0:
            x = quot + 1
            y = rest
        else:
            x = quot
            y = base

        return x, y

    def main(self):
        while self.user_on:
            print("\n----------------SUDOKU EM GRAFOS----------------\n")
            print("Seja bem-vindo ao gerador e solucionador de Sudokus.\n")
            print("Veja o menu abaixo e digite algum número indicado\npara seguir para a tela selecionada:")
            print()
            print("0 - Sair do programa")
            print("1 - Instruções de uso")
            print("2 - Solucionador passo-a-passo")
            print("3 - Gerador de Sudoku")
            print("4 - Solucionador de Sudoku")
            print("5 - Checador de Sudoku")

            user_in = input()
            user_in = int(user_in)

            if user_in == 0:
                self.user_on = False

            elif user_in == 1:
                self.tutorial_screen()
            
            elif user_in == 2:
                self.main_sudoku_solver_detailed()

            elif user_in == 3:
                self.main_sudoku_generator()

            elif user_in == 4:
                self.main_sudoku_solver()

            elif user_in == 5:
                self.main_sudoku_checker()

    def sudoku_graph_positions(self, base_size=9):
        return {i: i for i in range(1, (base_size**2) + 1)}

    def text_sudoku_positions(self, sudoku_redux):
        line_size = 34
        text_sudoku = "-"*line_size + "\n"

        for i in sudoku_redux.keys():
            lin_i, col_i = self.get_pos(i, 9)

            if col_i == 1:
                text_sudoku += "| "

            if len(str(sudoku_redux[i])) == 2:
                text_sudoku += str(sudoku_redux[i])
            else:
                text_sudoku += str(sudoku_redux[i]) + " "

            # Se for o último elemento da linha, não precisa de espaço, mas de quebramento de linha
            if col_i%9 != 0:
                text_sudoku += " "
            else:
                text_sudoku += " |\n"

            # Imprimir a divisão de blocos nas colunas
            if (col_i%3 == 0) and (col_i != 9):
                text_sudoku += "| "

            # Imprimir a divisão de blocos nas linhas
            if (lin_i%3 == 0) and (col_i%9==0) and (lin_i%9!=0):
                text_sudoku += "-"*line_size
                text_sudoku += "\n"

        text_sudoku += "-"*line_size

        return text_sudoku

    def print_sudoku_positions(self, base_size=9):
        sudoku_graph = self.sudoku_graph_positions(base_size)
        text_print = self.text_sudoku_positions(sudoku_graph)

        print(text_print)

    def sudoku_rules_text(self):
        print("-*-*-*-*-*-*-*-*-REGRAS DO SUDOKU-*-*-*-*-*-*-*-*-\n")
        print("- Tem o formato de uma matriz nXn;\n")
        print("- O jogo é composto por uma matriz composta de linhas,\ncolunas e blocos;\n")
        print("- Os blocos são grupos de células de tamanho n,\nabarcando todas as células a cada n linhas e colunas;\n")
        print("- Cada célula deve ser preenchida com números entre\n1 e n;\n")
        print("- Não é possível a repetição de números por linha,\ncoluna e bloco;\n")
        print("- Cada Sudoku tem apenas 1 solução possível.\n")

    def program_func_text(self):
        print("-*-*-*-*-*-*-*-FUNCIONALIDADES DO PROGRAMA-*-*-*-*-*-*-*-\n")
        print("- Gerar matrizes de Sudoku que podem ser resolvidas;\n")
        print("- Mostrar a solução de qualquer Sudoku dado;\n")
        print("- Checar se um Sudoku preenchido inserido é válido,\n")

    def program_func_intro_text(self):
        print("---------------------------------------------------------")
        print("\nPara entender as instruções do programa, tenha em mente\na seguinte matriz:\n")
        self.print_sudoku_positions()
        print("\nObserve que cada célula indica sua posição. É essa\na ordem dos Sudokus inseridos no programa.\n")
        print("Essa matriz será chamada de Sudoku de posições.\n")
        print("Confira abaixo as instruções para uso de cada uma das\nfuncionalidades do programa:\n")
        print("---------------------------------------------------------\n")
        
    def sudoku_solver_detailed_text(self):
        print("-----------------SOLUCIONADOR PASSO-A-PASSO-----------------\n")
        print("Opção para caso queira ver detalhadamente o funcionamento\ndo algoritmo de backtracking de coloração usado.\n")
        print("Aqui, o usuário pode apenas gerar Sudokus aleatórios e ver\nsuas soluções.\n")
        print("As opções que permitem inserção de dados do usuário no\nSudoku, logo abaixo, não mostram solução detalhada para\nnão poluir visualmente a interface do programa.\n")

    def sudoku_gen_text(self):
        print("-----------------GERADOR DE SUDOKU-----------------\n")
        print("No gerador de Sudoku, após ser entregue um Sudoku\npara o usuário resolver, é necessário inserir os\nvalores das células vazias, preenchidas em 0.\n")
        print("Nesse caso, o usuário deve inserir uma linha\nno seguinte formato:")
        print("\n(linha, coluna) - valor\n")
        print("No Sudoku com posições mostrado acima, o comando\n(2, 3) - 4 atribuirá à célula na posição 21 o\nvalor de 4.\n")

    def sudoku_solver_text(self):
        print("----------------SOLUCIONADOR DE SUDOKU----------------\n")
        print("Caso o usuário queira inserir um Sudoku para o programa\nresolver, ele deve se guiar pelo Sudoku de posições mostrado.\n")
        print("Assim, deve inserir célula a célula e apertar ENTER,\ncomeçando da primeira célula e terminando na célula 81.\n")
        print("As células vazias são representadas pelo valor 0.\n")

    def sudoku_checker_text(self):
        print("----------------CHECHADOR DE SUDOKU----------------\n")
        print("No checador de Sudoku, o usuário deve inserir um\nSudoku completamente preenchido.\n")
        print("Assim como no solucionador, deve seguir a ordem\ndo Sudoku de posições. A única diferença é que\nnão há células com 0.\n")

    def tutorial_text(self):
        self.sudoku_rules_text()
        self.program_func_text()
        self.program_func_intro_text()
        self.sudoku_solver_detailed_text()
        self.sudoku_gen_text()
        self.sudoku_solver_text()
        self.sudoku_checker_text()

    def tutorial_screen(self):
        print()
        self.tutorial_text()

        print("Digite qualquer tecla para retornar ao menu inicial.\n")
        input()
        
    def get_index_by_pos(self, row, col, base):
        return col + (base*(row-1))

    def fill_cell_input(self, user_input, base_size=9):
        if ("(" not in user_input) or (")" not in user_input) or ("," not in user_input) or ("-" not in user_input):
            return 0

        pos, val = user_input.replace(" ", "").split("-")
        pos_x, pos_y = pos.replace("(", "").replace(")", "").split(",")

        pos_x = int(pos_x)
        pos_y = int(pos_y)
        val = int(val)

        if (val < 0) or (val > 9):
            return 1

        index_in_graph = self.get_index_by_pos(pos_x, pos_y, base_size)

        return [index_in_graph, val]
    
    def main_sudoku_solver_detailed(self):
        print("")
        print("Aqui será gerado um Sudoku aleatório e sua solução será feita.")
        print("O passo-a-passo da solução com backtracking será imprimido.")
        print("")
        print("0 - Retornar ao menu principal")
        print("1 - Iniciar solucionador detalhado")
        print("")

        user_in = input()
        user_in = int(user_in)

        if user_in == 0:
            return
        else:
            self.started_sudoku_solver_detailed()

    def started_sudoku_solver_detailed(self):
        print()
        print()
        print("O Sudoku gerado será exibido abaixo.")
        print("Digite a opção que deseja:")
        print("")
        print("0 - Interromper solucionador")
        print("1 - Mostrar solução")
        print("2 - Gerar novo Sudoku")
        print()

        while True:

            gen_sudoku = SudokuUser(9)
            gen_sudoku.gen_empty_sudoku()
            gen_sudoku.gen_random_sudoku()
            gen_sudoku.print_sudoku()

            user_in = input()

            if (user_in == "0") or (user_in == "1") or (user_in == "2"):
                user_in = int(user_in)

                if user_in == 0:
                    return

                elif user_in == 1:
                    print("O passo-a-passo da solução com backtracking pode ser visto abaixo:\n")
                    gen_sudoku.solve_sudoku(print_steps=True)

                    print("\n\n")
                    print("A solução para o Sudoku é:\n")
                    gen_sudoku.print_sudoku()

                    print("Digite qualquer tecla para retornar ao menu inicial.\n")
                    input()
                    
                    return

                elif user_in == 2:
                    print("O novo Sudoku gerado pode ser visto abaixo.")

            else:
                fill_in = self.fill_cell_input(user_in)

                if fill_in == 0:
                    print("Comando inválido. Digite novamente algum comando.\n")

                elif fill_in == 1:
                    print("Número precisa ser entre 1 e 9. Digite novamente.\n")

                else:
                    if gen_sudoku.fill_cell(fill_in[0], fill_in[1]):
                        print("Célula preenchida com sucesso. Digite algum comando.\n")
                    else:
                        print("Célula dada no Sudoku, impossível de alterar. Digite algum comando.\n")
    
    def main_sudoku_generator(self):
        print("")
        print("Para mexer no gerador de Sudoku, leia o menu\nabaixo e digite a opção para o serviço que quer:")
        print("")
        print("0 - Retornar ao menu principal")
        print("1 - Iniciar gerador")
        print("")

        user_in = input()
        user_in = int(user_in)

        if user_in == 0:
            return
        else:
            self.started_sudoku_generator()

    def started_sudoku_generator(self):
        print()
        print()
        print("O Sudoku gerado será exibido abaixo.")
        print("Para preencher uma célula digite: (x, y) - val")
        print("Onde x é o número da linha, y da coluna e val o valor da célula, entre 1 e 9.")
        print("Além dos comandos de preenchimento de célula, há 3 comandos principais:")
        print("")
        print("0 - Interromper gerador")
        print("1 - Imprimir Sudoku")
        print("2 - Checar solução")
        print("3 - Mostrar solução")
        print("4 - Gerar novo Sudoku")

        gen_sudoku = SudokuUser(9)
        gen_sudoku.gen_empty_sudoku()
        gen_sudoku.gen_random_sudoku()
        gen_sudoku.print_sudoku()
        
        while True:
            
            user_in = input()

            if (user_in == "0") or (user_in == "1") or (user_in == "2") or (user_in == "3") or (user_in == "4"):
                user_in = int(user_in)

                if user_in == 0:
                    return

                elif user_in == 4:
                    print("O novo Sudoku gerado pode ser visto abaixo:")
                    
                    gen_sudoku = SudokuUser(9)
                    gen_sudoku.gen_empty_sudoku()
                    gen_sudoku.gen_random_sudoku()
                    gen_sudoku.print_sudoku()

                elif user_in == 2:
                    if gen_sudoku.solution_checker():
                        print("Solução correta.")
                    else:
                        print("Solução incorreta.")

                elif user_in == 3:
                    gen_sudoku.solve_sudoku()

                    print()
                    print("A solução para o Sudoku é:\n")
                    gen_sudoku.print_sudoku()
                    
                    print("Digite qualquer tecla para retornar ao menu inicial.\n")
                    input()
                    
                    return

                elif user_in == 1:
                    print()
                    gen_sudoku.print_sudoku()
                    print()

            else:
                fill_in = self.fill_cell_input(user_in)

                if fill_in == 0:
                    print("Comando inválido. Digite novamente algum comando.\n")

                elif fill_in == 1:
                    print("Número precisa ser entre 1 e 9. Digite novamente.\n")

                else:
                    if gen_sudoku.fill_cell(fill_in[0], fill_in[1]):
                        print("Célula preenchida com sucesso. Digite algum comando.\n")
                    else:
                        print("Célula dada no Sudoku, impossível de alterar. Digite algum comando.\n")
                        
    def get_user_sudoku(self, base_size=9):
        user_sudoku_graph = {i: 0 for i in range(1, (base_size**2)+1)}

        for i in range(1, len(user_sudoku_graph.keys())+1):
            valid_input = False

            while not valid_input:
                user_input = input(str(i) + ": ")

                try:
                    user_input = int(user_input)

                    if user_input == -1:
                        return False

                    if (user_input >= 0) and (user_input <= 9):
                        user_sudoku_graph[i] = user_input
                        valid_input = True
                    else:
                        print("Valor inválido. Insira novamente.")

                except:
                    print("Valor inválido. Insira novamente.")

        return user_sudoku_graph
    
    def main_sudoku_solver(self):
        print()
        print("Para mexer no solucionador de Sudoku, leia o menu abaixo e digite a opção desejada:")
        print()
        print("-2 - Retornar ao menu inicial")
        print("-1 - Interromper inserção")
        print("0 - Iniciar inserção de Sudoku")
        print()

        while True:
            user_in = input()
            user_in = int(user_in)

            if user_in == -2:
                return

            elif user_in == 0:
                user_sudoku = self.sudoku_solver()
                print("\nDigite alguma tecla para retornar ao menu inicial.")
                input()
                return

            else:
                print("Número inválido. Digite -2 ou 0.")

    def sudoku_solver(self, base_size=9):
        user_sudoku_redux = self.get_user_sudoku(base_size)

        if user_sudoku_redux == False:
            return False

        user_sudoku = SudokuUser(base_size)
        user_sudoku.fill_given_sudoku(user_sudoku_redux)

        user_sudoku.solve_sudoku()

        print("\nA solução do Sudoku dado pode ser vista abaixo:\n")
        user_sudoku.print_sudoku()
        
    def main_sudoku_checker(self):
        print()
        print()
        print("Cada número preenchido será uma célula do Sudoku.")
        print("Caso queira interromper a inserção e/ou retornar\nao menu anterior, digite os comandos:")
        print("")
        print("-2 - Retornar ao menu inicial")
        print("-1 - Interromper inserção")
        print("0 - Iniciar inserção de Sudoku")
        print()

        while True:
            user_in = input()
            user_in = int(user_in)

            if user_in == -2:
                return

            elif user_in == 0:
                user_sudoku = self.sudoku_checker()
                print("\nDigite alguma tecla para retornar ao menu inicial.")
                input()
                return

            else:
                print("Número inválido. Digite -2 ou 0.")
            
    def sudoku_checker(self, base_size=9):
        user_sudoku_redux = self.get_user_sudoku(base_size)

        if user_sudoku_redux == False:
            return False

        user_sudoku = SudokuUser(base_size)
        user_sudoku.fill_given_sudoku(user_sudoku_redux)

        if user_sudoku.solution_checker() != False:
            print("\nA solução dada é válida.\n")
        else:
            print("\nA solução dada não é válida.\n")


user_program = UserInterface()
user_program.main()