import socket, struct, os

IP = ""
PORTA = 8080
FORMATO_CABECALHO = "!IIB"
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

print(f'O tamanho do cabeçalho é: {TAMANHO_CABECALHO} bytes.')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((IP, PORTA))

print(f'[*] Servidor UDP aguardando arquivos em {IP} : {PORTA}...')



seq_esperado = 0
arquivo_destino = open('arquivo.pdf', 'wb')
transacao_atual = None


try:
    while True:
        # Recebendo dados
        # Buffer maior que o MTU
        pacote, endereco_cliente = sock.recvfrom(2048)


        # Separar o cabeçalho do payload
        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]

        #Desem



