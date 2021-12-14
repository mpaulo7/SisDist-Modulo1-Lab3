# Exemplo basico socket (lado passivo)

import socket
import os.path
import select
import sys
import threading


TERMO_NAO_ENCONTRADO = "Termo não encontrado no arquivo" # Mensagem padrão para termo não encontrado no arquivo
ARQUIVO_NAO_ENCONTRADO = "Arquivo não encontrado" # Mensagem padrão para arquivo não encontrado

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena as conexoes completadas
conexoes = {}
#lock para acesso do dicionario 'conexoes'
lock = threading.Lock()

def iniciaServidor():
    '''Cria um socket de servidor e o coloca em modo de espera por conexoes
    Saida: o socket criado'''
    # cria o socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

    # vincula a localizacao do servidor
    sock.bind((HOST, PORTA))

    # coloca-se em modo de espera por conexoes
    sock.listen(5) 

    # configura o socket para o modo nao-bloqueante
    sock.setblocking(False)

    # inclui o socket principal na lista de entradas de interesse
    entradas.append(sock)

    return sock

def aceitaConexao(sock):
    '''Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente'''

    # estabelece conexao com o proximo cliente
    clisock, endr = sock.accept()

    # registra a nova conexao
    lock.acquire()
    conexoes[clisock] = endr 
    lock.release()

    return clisock, endr

def atendeRequisicoes(clisock, endr):
    '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente
    Saida: '''

    while True: 
        # depois de conectar-se, espera o nome do arquivo 
        nomeArquivo = clisock.recv(1024)
        
        # espera o termo de busca
        termo = clisock.recv(1024)
        
        if not nomeArquivo: 
            print(str(endr) + '-> encerrou')
            lock.acquire()
            del conexoes[clisock] #retira o cliente da lista de conexoes ativas
            lock.release()
            clisock.close() # encerra a conexao com o cliente
            return
        else:
            # verifica se o arquivo existe
            if os.path.isfile(nomeArquivo):
                # abre o arquivo e o lê na variável conteudo, fechando-o em seguida
                arquivo = open(nomeArquivo)
                conteudo = arquivo.read()
                arquivo.close()
                
                # conta quantas vezes o termo está presente no arquivo, montando o resultado
                qtd = conteudo.count(str(termo,  encoding='utf-8'))
                if qtd > 0:
                    resultado = "Termo encontrado " + str(qtd) + " vezes no arquivo."
                else:
                    # termo não encontrado no arquivo
                    resultado = TERMO_NAO_ENCONTRADO
            else:
                # arquivo não existe
                resultado = ARQUIVO_NAO_ENCONTRADO
                
        
        # envia mensagem de resposta
        clisock.sendall(bytes(resultado, 'utf-8')) 
    clisock.close()


def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
    sock = iniciaServidor()
    print("Pronto para receber conexoes...")
    while True:
        #espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        #tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == sock:  #pedido novo de conexao
                clisock, endr = aceitaConexao(sock)
                print ('Conectado com: ', endr)
                #cria nova thread para atender o cliente
                cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr))
                cliente.start()
            elif pronto == sys.stdin: #entrada padrao
                cmd = input()
                if cmd == 'fim': #solicitacao de finalizacao do servidor
                    if not conexoes: #somente termina quando nao houver clientes ativos
                        sock.close()
                        sys.exit()
                    else: print("ha conexoes ativas")
                elif cmd == 'hist': #outro exemplo de comando para o servidor
                    print(str(conexoes.values()))

main()

