# Laboratório 1 - Marcos Paulo Moraes

import socket

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

arquivo = input("Informe o nome de um arquivo (para parar, envie STOP): ")

while (arquivo != "STOP"):

    # envia o nome do arquivo para o par conectado
    sock.sendall(bytes(arquivo,'UTF-8'))
    
    termo = input("Informe o termo de busca no arquivo: ")
    #mensagem = arquivo + ":" + termo
    
    # envia o termo de busca para o par conectado
    sock.sendall(bytes(termo,'UTF-8'))
    
    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem

    # imprime a mensagem recebida
    print(str(msg,  encoding='utf-8'))
    
    arquivo = input("Informe o nome de um arquivo (para parar, envie STOP): ")

# encerra a conexao
sock.close() 
