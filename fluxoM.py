import os
import sys
import networkx as nx
import random
import re

# função geradora de grafo
def gera_grafo(arquivo):
    # Obtém o diretório do arquivo Python atual
    diretorio_atual = os.path.dirname(__file__)

    # Calcula o caminho relativo ao arquivo
    nome_arquivo = os.path.join(diretorio_atual, "./instancias/" + arquivo)
    # declaração da matriz inicial auxiliar vazia
    matriz = []

    # Abre o arquivo para leitura se o arquivo não existir retorna uma mensagem de erro e encerra o programa
    try:
        with open(nome_arquivo, "r") as arquivo:
            # Lê o valor da primeira linha (quantidade de vertices) e o converte para int
            vertices = int(arquivo.readline().strip())

            # Lê o restante das linhas do arquivoos converte para int e os adiciona na matriz auxiliar
            cont = 1
            for linha in arquivo:
                cont += 1
                valores = linha.split()
                valores = [int(valor) for valor in valores]
                matriz.append(valores)
    except:
        print("Arquivo não encontrado")
        exit()
    # coleta os vertices
    num_vertices = [i + 1 for i in range(vertices)]

    # Cria um grafo direcionado com a biblioteca NetworkX
    G = nx.DiGraph()

    # Adicione nós e arestas ao grafo
    G.add_nodes_from(num_vertices)

    # Adiciona as arestas com os pesos
    edges = [(origem, destino, {"capacity": peso}) for origem, destino, peso in matriz]
    G.add_edges_from(edges)

    return G

# função geradora de todos os caminhos
def gera_todos_os_caminhos(G, origem, destino):
    caminhos = []
    for path in nx.all_simple_paths(G, source=origem, target=destino):
        path_properties = [(u, v, G[u][v]["capacity"]) for u, v in zip(path, path[1:])]
        caminhos.append(path_properties)
    if len(caminhos) < 1:
        return None, 0
    else:
        return caminhos, len(caminhos)

# função geradora de individuos (subgrafo)
def gera_individuo(caminhos):
    SG = nx.DiGraph()
    if len(caminhos) > 1:
        caminhos_escolhidos = random.sample(caminhos,2)
    else:
        caminhos_escolhidos = caminhos  
        
    for caminho in caminhos_escolhidos:
        for i in range(len(caminho)):
            u, v, peso = caminho[i]
            SG.add_edge(u, v, capacity=peso)
    SG.genes = caminhos_escolhidos
    return SG

# individuo mutado ou filho
def novo_individuo(caminhos):
    SG = nx.DiGraph()
    for caminho in caminhos:
        for i in range(len(caminho)):
            u, v, peso = caminho[i]
            SG.add_edge(u, v, capacity=peso)
    return SG

# função calcula fluxo do subgrafo
def calcula_fluxo_induviduo(SG, origem, destino):
    valor_fluxo, _ = nx.maximum_flow(SG, origem, destino)
    return valor_fluxo

# função calcula fluxo da geração
def calcula_fluxo_geracao(populacao, origem, destino):
    fluxos = []
    for individuo in populacao:
        fluxo = calcula_fluxo_induviduo(individuo, origem, destino)
        fluxos.append([individuo, {"fluxo": fluxo}, {"genes": individuo.genes}])
    return fluxos

# função calcula melhor individuo da geração (maior fluxo)
def melhores_individuos_geracao(fluxos_geracao):
    melhor_individuo = max(fluxos_geracao, key=lambda x: x[1]["fluxo"])
    fluxos_geracao.remove(melhor_individuo)
    segundo_melhor_individuo = max(fluxos_geracao, key=lambda x: x[1]["fluxo"])
    return melhor_individuo, segundo_melhor_individuo

# função geradora de populacao inicial
def gera_populacao_inicial(tamanho_populacao, caminhos):
    populacao_inicial = []
    for i in range(tamanho_populacao):
        populacao_inicial.append(gera_individuo(caminhos))
    return populacao_inicial

# função de mutação
def mutacao(individuo, caminhos):
    print
    numero_aleatorio = random.random()
    genes = []
    individuo_mutado = []
    # mutação por remoção
    if numero_aleatorio <= 1 / 3:
        if (len(individuo[2]["genes"]) > 1):
            for i in range(len(individuo[2]["genes"])//2):
                individuo[2]["genes"].remove(random.choice(individuo[2]["genes"]))
        else:
            if len(caminhos) <= 1:
                pass
            else:
                individuo[2]["genes"].remove(random.choice(individuo[2]["genes"]))
                individuo[2]["genes"].append(random.choice(caminhos))
    # mutação por adição
    elif numero_aleatorio > 1 / 3 and numero_aleatorio <= 2 / 3:
        if (len(individuo[2]["genes"]) > 1):
            for i in range(len(individuo[2]["genes"])//2):
                individuo[2]["genes"].append(random.choice(caminhos))
        else:
            if len(caminhos) <= 1:
                pass
            individuo[2]["genes"].append(random.choice(caminhos))
    # mutação por substituição
    else:
        if (len(individuo[2]["genes"]) > 1):
            quant_genes = len(individuo[2]["genes"])//2  
            for i in range(quant_genes):
                individuo[2]["genes"].remove(random.choice(individuo[2]["genes"]))

            for i in range(quant_genes):
                individuo[2]["genes"].append(random.choice(caminhos))
        else:
            if len(caminhos) <= 1:
                pass
            else:
                individuo[2]["genes"].remove(random.choice(individuo[2]["genes"]))
                individuo[2]["genes"].append(random.choice(caminhos))
        
    genes = individuo[2]["genes"]
    individuo_mutado = novo_individuo(genes)

    return [individuo_mutado, {"fluxo": calcula_fluxo_induviduo(individuo_mutado, origem, destino)}, {"genes": genes}]

# função de cruzamento
def cruzamento(reprodutor, individuo, origem, destino):
    filho = None
    genes_filho = []
    genes_individuo = []

    # tipo de cruzamento: 50|50
    if len(reprodutor[2]["genes"]) > 1:
        random.shuffle(reprodutor[2]["genes"])
        genes_reprodutor = reprodutor[2]["genes"][:(len(reprodutor[2]["genes"])//2)]
    else:
        genes_reprodutor = reprodutor[2]["genes"]
    
    if len(individuo[2]["genes"]) > 1:
        random.shuffle(individuo[2]["genes"])
        genes_individuo = individuo[2]["genes"][:len(individuo[2]["genes"])//2]
    else:
        genes_individuo = individuo[2]["genes"]
        
    genes_filho = genes_reprodutor + genes_individuo

    filho = novo_individuo(genes_filho)

    return ([filho, {"fluxo": calcula_fluxo_induviduo(filho, origem, destino)}, {"genes": genes_filho}])

# gera nova geração
def nova_geracao(populacao, chance_mutacao, chance_reproducao, origem, destino, caminhos):
    # parametros
    nova_geracao = []
    filhos = []
    individuos_mutados = []
    melhor_individuo = []
    segundo_melhor_individuo = []
    geracao = []
    
    # Calcula o fluxo da geração
   
    # ordena a população pelo fluxo maior
    populacao.sort(key=lambda x: x[1]["fluxo"], reverse=True)
    
    # define melhor e segundo melhor indivíduo e os remove da geracao anterior
    melhor_individuo = populacao[0]
    populacao.remove(populacao[0])
    segundo_melhor_individuo = populacao[0]
    # print(segundo_melhor_individuo)
    populacao.remove(populacao[0])

    # adiciona os dois melhores individuos da geração anterior
    geracao.append(melhor_individuo)
    # adiciona os filho dos dois melhores individuos da geração anterior
    geracao.append(cruzamento(melhor_individuo, segundo_melhor_individuo, origem, destino))

    # calcula os demais filhos e individuos mutados
    for i in populacao:
        numero_aleatorio1 = random.random()
        numero_aleatorio2 = random.random()
        if numero_aleatorio1 <= chance_reproducao:
            filhos.append(cruzamento(melhor_individuo, i, origem, destino))
        elif numero_aleatorio2 <= chance_mutacao:
            individuos_mutados.append(mutacao(i, caminhos))
        else:
            numero_aleatorio3 = random.random()
            if numero_aleatorio3 <= 0.5:
                filhos.append(cruzamento(melhor_individuo, i, origem, destino))
            else:
                individuos_mutados.append(mutacao(i, caminhos))
    
    nova_geracao = geracao
    nova_geracao.extend(filhos)
    nova_geracao.extend(individuos_mutados)
   
    return nova_geracao, max(nova_geracao, key=lambda x: x[1]["fluxo"])    

# função principal
def main():
    # gera a população inicial    
    populacao_inicial = gera_populacao_inicial(tamanho_populacao, caminhos)

    # calcula o fluxo da população inicial
    populacao_atual = calcula_fluxo_geracao(populacao_inicial, origem, destino)
    
    # Executa o algoritmo genético
    print("inicial algoritmo")
    for i in range(quantidade_geracoes):
        populacao_atual, individuo_fluxo_maximo_atual = nova_geracao(populacao_atual, probabilidade_mutacao, probabilidade_cruzamento, origem, destino, caminhos)
        print(f"Geração: {i+1} Fluxo maximo {individuo_fluxo_maximo_atual[1]["fluxo"]}.")

    # mostra o resultado
    print("Fluxo máximo encontrado:", individuo_fluxo_maximo_atual[1]["fluxo"])
    
############################ CÓDIGO ############################
# Configurar leitura dos parâmetros
params = sys.argv[1:]
padrao = r"(-read [^\s]+ -nodes \d+ \d+ -pi \d+ -qg \d+( --probs \d+ \d+)?+( -confg)?)|(-help)"
exe = False

if re.match(padrao, " ".join(params)):
    arquivo = None
    tamanho_populacao = None
    quantidade_geracoes = None
    probabilidade_mutacao = 0.7
    probabilidade_cruzamento = 0.4

    # Lendo os parâmetros e configurando as variáveis
    for text in params:

        # Verificando o tipo de parâmetro
        if text == '-help':
            print("\nPara executar o programa, digite um comando no formato:\npy fluxoM.py -read <arquivo> -nodes <origem> <destino> -pi <tamanho_populacao> -qg <quantidade_geracoes> --probs <probabilidade_mutacao> <probabilidade_cruzamento>")
            print("\nExemplo:\npy fluxoM.py -read fluxo-inst13 -nodes 1 3 -pi 10 -qg 10 --probs 60 40\n")
            print("O parâmetro --probs não é obritório, caso não seja informado, o programa utilizará as configurações padrão (70% de mutação e 40% de cruzamento).\n")
            break
        if text == '-read':
            try:
                pasta_arquivos = "./instancias"
                arquivos_disponiveis = os.listdir(pasta_arquivos)
                # Lendo o nome do arquivo no console e armazenando na variável
                arquivo = sys.argv[2]
                if arquivo not in arquivos_disponiveis:
                    print(f"O arquivo ({arquivo}) não foi encontrado. Tente novamente.")
                    break

            except:
                # Tratando o erro de arquivo não encontrado
                print(f"Deu ruim: {err}")
                break
        try:
            # Verificando o tipo de parâmetro
            if text == '-nodes':
                exe = True

                origem = int(sys.argv[4])
                destino = int(sys.argv[5])
                
                # grafo geral
                G = gera_grafo(arquivo)
    
                # Verificando se os valores de origem e destino são válidos
                # calcula todos os caminhos e verifica se existe caminho entre a origem e o destino termina o programa se não existir
                caminhos, quant_caminhos = gera_todos_os_caminhos(G, origem, destino)            
                # Tratando os tipos de visualizações permitidas
                if caminhos == None:
                    print(f"Não existe caminhos entre os vétices {origem} e {destino}")
                    break
        
            if text == '-pi':
                tamanho_populacao = int(sys.argv[7])
                
            if text == '-qg':
                quantidade_geracoes = int(sys.argv[9])
            
            if text == '--probs':
                probabilidade_mutacao = int(sys.argv[11])/100
                probabilidade_cruzamento = int(sys.argv[12])/100
   
        except Exception as err:
            print(err)
    if exe:  
        main()
else:
    print("Comando inválido. Digite 'py fluxoM.py help' para obter ajuda.")

################## EXEMPLO ##################
# py fluxoM.py -read fluxo-inst13 -nodes 1 6 -pi 10 -qg 10 --probs 60 40 
