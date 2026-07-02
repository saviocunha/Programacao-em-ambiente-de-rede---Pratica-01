import socket, struct, os, random

IP = ""
PORTA = 8080
FORMATO_CABECALHO = "!IIB"
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))


#--- TAREFA A -- Servidor inicia sem timeout
sock.settimeout(None)

print(f'[*] Servidor UDP aguardando arquivos em {IP} : {PORTA}...')

seq_esperado = 0
# arquivo_destino = open('arquivo.pdf', 'wb') 
# ---- TAREFA A ----
nome_arquivo = 'arquivo.pdf'    # Variável que vai guardar o nome do arquivo a ser criado
arquivo_destino = None          # O arquivo será criado somente quando o primeiro pacote chegar     

transacao_atual = None

try:
    while True:
        pacote, endereco_cliente = sock.recvfrom(2048)

        # --- Tarefa B - Simulador de rede ruim 
        if random.random() < 0.3: # 30 % de chance de "perder" o pacote
            print('[SIMULAÇÃO] Ops, pacote perdido na rede...')
            continue


        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]

        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        if transacao_atual is None:
            transacao_atual = trans_id

            # --TAREFA A-- Cria o arquivo somente quando a transferência começa
            arquivo_destino = open(nome_arquivo, 'wb')

            # -- TAREFA A -- Timeout de 10 s.
            sock.settimeout(10)


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


# --- TAREFA A --- Lógica do timeout. Cliente desistiu ou caiu
except socket.timeout:
    print('[!] Timeout! Cliente parou de enviar dados.')

    # --- TAREFA A --- Verifica se um arquivo foi aberto antes de fecha-lo
    if arquivo_destino is not None:
        arquivo_destino.close()
    
    # --- TAREFA A --- Verifica se um arquivo existe no diretório antes de apaga-lo
    if os.path.exists('arquivo.pdf'):
        os.remove(nome_arquivo)
        print('[*] Arquivo incompleto removido.')


except KeyboardInterrupt:
    print("\n [*] Servidor encerrado pelo usuário.")
    
    # --- TAREFA A --- Verifica se um arquivo foi aberto e se ele ainda não foi fechado
    if arquivo_destino is not None and not arquivo_destino.closed:
        arquivo_destino.close()
    


