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

        #Desempacotar o cabeçalho
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        # Se for o primeiro pacote, registramos os trans_id
        if transacao_atual is None:
            transacao_atual = trans_id

        # Verifica se o pacote pertence à transação atual
        if trans_id != transacao_atual:
            continue # Ignora pacotes alienígenas

        # Lógica de ordenação e ACK
        if seq_num == seq_esperado:
            print(f"[+] Recebido pacote {seq_num}. Gravando no disco ...")
            arquivo_destino.write(payload)
            seq_esperado += 1

            # Enviar ACK correspondente
            ack_pacote = struct.pack("!I", seq_num)
            sock.sendto(ack_pacote, endereco_cliente)


            # Verificar se é o último pacote
            if flag ==1:
                print('[*] Último pacote recebido. Transferência concluída.')
                arquivo_destino.close()
                break # Saí do loop
        else:
            # TODO: o que fazer se receber um pacote duplicado ou fora de ordem?
            # DICA: O cliente pode estar retransmitindo ou perdeu o seu ACK
            # Você deve reenviar o ACK do pacote anterior.
            pass

except KeyboardInterrupt:
    print("\n [*] Servidor encerrado.")
    arquivo_destino.close()





