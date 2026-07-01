import socket, struct, os, random

IP_DESTINO = "127.0.0.1"
PORTA_DESTINO = 8080

# Coloque um arquivo PDF real na mesma pasta
# altere o nome do arquivo de acordo com o código
# ou altere o código de acordo com o nome do arquivo 


NOME_ARQUIVO = "meu_arquivo.pdf"

TAMANHO_PAYLOAD = 1024
FORMATO_CABECALHO = "!IIB"


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definindo o Timeout. Se recvfrom demorar mais de 1 segundo,
# gera erro (exceção)

sock.settimeout(1.0)


trans_id = random.randint(1000, 9999)
seq_num = 0

print(f'[*] Iniciando transferência de {NOME_ARQUIVO}')
print(f'[*] ID da transação: {trans_id}')



with open(NOME_ARQUIVO, 'rb') as arquivo:
    while True:
        # Ler um pedaço do arquivo
        pedaco = arquivo.read(TAMANHO_PAYLOAD)

        # Lógica para descobrir se é o último pacote
        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD or not pedaco else 0

        if not pedaco and flag == 0:
            break # Fim do arquivo
        

        # Montar o pacote
        cabecalho = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag)
        pacote_completo = cabecalho + pedaco

        ack_recebido = False
        tentativas = 0
        MAX_TENTATIVAS = 5


        # Loop do Stop-and-Wait (retransmissão)
        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                # Enviar o pacote completo
                sock.sendto(pacote_completo, (IP_DESTINO, PORTA_DESTINO))
                print(f'[>] Pacote {seq_num} enviado. Aguardando ACK...(Tentativa {tentativas+1})')

                # Aguardar o ACK    
                ack_pacote, _ = sock.recvfrom(4) # Espera 4 bytes (o strunct "!I")
                
                # Simulador de perda de ACK
                if random.random() < 0.3: 
                    print("[SIMULAÇÃO] ACK perdido na rede...")
                    raise socket.timeout() 

                ack_num = struct.unpack('!I', ack_pacote) [0]


                if ack_num == seq_num:
                    print(f'[<] ACK {ack_num} recebido!')
                    ack_recebido = True
                    seq_num += 1
                else:
                    print(f'[-] ACK incorreto recebido. Ignorando.')

            except socket.timeout:
                print(f'[!] Timeout! Não recebi o ACK do pacote {seq_num}.')
                tentativas += 1

            except ConnectionResetError:
                print(f'[-] Erro: Conexão resetada pelo receptor. Tentando novamente...')
                tentativas = MAX_TENTATIVAS  # Força a saída do loop para encerrar a transferência
                break
                    
        if tentativas == MAX_TENTATIVAS:
            print('[-] Limite de retransmissões atingido. Conexão perdida.')
            break # Aborta a transferência

        if flag == 1:
            print("[+] Transferência finalizada com sucesso.")
            break

