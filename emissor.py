import socket
import struct
import os
import random

IP_DESTINO = "127.0.0.1"
PORTA_DESTINO = 8080

NOME_ARQUIVO = "meu_arquivo.pdf"

TAMANHO_PAYLOAD = 1024
FORMATO_CABECALHO = "!IIB"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)

trans_id = random.randint(1000, 9999)
seq_num = 0

print(f'[*] Iniciando transferência de {NOME_ARQUIVO}')
print(f'[*] ID da transação: {trans_id}')

with open(NOME_ARQUIVO, 'rb') as arquivo:
    while True:
        pedaco = arquivo.read(TAMANHO_PAYLOAD)

        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD or not pedaco else 0

        if not pedaco and flag == 0:
            break
        
        cabecalho = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag)
        pacote_completo = cabecalho + pedaco

        ack_recebido = False
        tentativas = 0
        MAX_TENTATIVAS = 5

        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                sock.sendto(pacote_completo, (IP_DESTINO, PORTA_DESTINO))
                print(f'[>] Pacote {seq_num} enviado. Aguardando ACK...(Tentativa {tentativas+1})')

                # --- Tarefa B - Simulador de rede ruim 
                if random.random() < 0.3: # 30 % de chance de "perder" o pacote
                    print('[SIMULAÇÃO] Ops, pacote perdido na rede...')
                    continue
                
                
                
                ack_pacote, _ = sock.recvfrom(4)

                ack_num = struct.unpack('!I', ack_pacote)[0]

                if ack_num == seq_num:
                    print(f'[<] ACK {ack_num} recebido!')
                    ack_recebido = True
                    seq_num += 1
                else:
                    print(f'[-] ACK incorreto recebido. Ignorando.')

            except socket.timeout:
                print(f'[!] Timeout! Não recebi o ACK do pacote {seq_num}.')
                tentativas += 1
        
        if tentativas == MAX_TENTATIVAS:
            print('[-] Limite de retransmissões atingido. Conexão perdida.')
            break

        if flag == 1:
            print("[+] Transferência finalizada com sucesso.")
            break
