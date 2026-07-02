
import socket
import struct
import os
import random

IP = ""

PORTA = 8080


FORMATO_CABECALHO = "!IIB"

TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((IP, PORTA))

sock.settimeout(10.0)  #Define aqui um timeout de 10 segundos para operações de recebimento (Rollback)

print(f'[*] Servidor UDP aguardando arquivos em {IP} : {PORTA}...')

seq_esperado = 0  
arquivo_destino = open('recebido.pdf', 'wb')  
transacao_atual = None  


try:
    while True:
        try:
            # Recebendo dados
            # Buffer de 2048 bytes é maior que o MTU padrão (1500), garantindo leitura do pacote cheio
            pacote, endereco_cliente = sock.recvfrom(2048)
            
            if random.random() < 0.3: #Simulação de perda de pacotes com taxa de 30%
                print("[SIMULAÇÃO] Pacote perdido na rede...")
                continue

        # Essa parte aqui é o rollback com timeout de 10 segundos.
        except socket.timeout:
            print("\n[!] Timeout de 10 segundos atingido. Encerrando a sessão...")
            arquivo_destino.close()  # Fecha o arquivo para evitar corrupção
            if os.path.exists("recebido.pdf"):
                os.remove("recebido.pdf")  # Remove o arquivo incompleto
                print("[-] Arquivo incompleto removido (Rollback).")
            break  

        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]

        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        if transacao_atual is None:
            transacao_atual = trans_id

        if trans_id != transacao_atual:
            continue 

        if seq_num == seq_esperado:
            print(f"[+] Recebido pacote {seq_num}. Gravando no disco ...")
            arquivo_destino.write(payload)  
            seq_esperado += 1  

          
            ack_pacote = struct.pack("!I", seq_num)
            sock.sendto(ack_pacote, endereco_cliente)

           
            if flag == 1:
                print('[*] Último pacote recebido. Transferência concluída.')
                arquivo_destino.close() 
                break 
        else:
          
            if seq_num < seq_esperado:
                ack_pacote = struct.pack("!I", seq_num)
                sock.sendto(ack_pacote, endereco_cliente)

# Essa parte aqui é o rollback em caso de fechamento abrupto do servidor
except KeyboardInterrupt:
    print("\n [*] Servidor encerrado pelo usuário.")
    arquivo_destino.close()  # Garante que o arquivo não fique corrompido ao fechar

    if os.path.exists("recebido.pdf"):
        os.remove("recebido.pdf")  # Remove o arquivo incompleto
