import socket
import struct
import os

IP = ""
PORTA = 8080

FORMATO_CABECALHO = "!IIB"
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

# ALTERAÇÃO (Tarefa A): tempo máximo, em segundos, que o servidor espera
# por um novo pacote antes de considerar a transação abandonada.
TIMEOUT_TRANSACAO = 10.0


# ALTERAÇÃO: trecho de envio de ACK que antes estava repetido duas vezes
# dentro do loop foi extraído para esta função (modularização).
def enviar_ack(sock, endereco, seq_num):
    ack_pacote = struct.pack("!I", seq_num)
    sock.sendto(ack_pacote, endereco)


# ALTERAÇÃO (Tarefa A): função nova. Fecha e apaga o arquivo incompleto
# do disco quando a transação é abortada por timeout.
def abortar_transacao(arquivo_destino):
    nome = arquivo_destino.name
    arquivo_destino.close()
    if os.path.exists(nome):
        os.remove(nome)
        print(f"[!] Timeout de {TIMEOUT_TRANSACAO}s sem pacotes. "
              f"Arquivo incompleto '{nome}' removido do disco.")


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))
# ALTERAÇÃO (Tarefa A): timeout no socket para detectar cliente inativo.
sock.settimeout(TIMEOUT_TRANSACAO)

print(f'[*] Servidor UDP aguardando arquivos em {IP}:{PORTA}...')

seq_esperado = 0
arquivo_destino = open('recebido.pdf', 'wb')
transacao_atual = None

try:
    while True:
        # ALTERAÇÃO (Tarefa A): recvfrom agora pode estourar timeout.
        # Se estourar e já havia transação em andamento, aborta e apaga o arquivo.
        try:
            pacote, endereco_cliente = sock.recvfrom(2048)
        except socket.timeout:
            if transacao_atual is not None:
                abortar_transacao(arquivo_destino)
                break
            continue

        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        if transacao_atual is None:
            transacao_atual = trans_id

        if trans_id != transacao_atual:
            continue

        if seq_num == seq_esperado:
            print(f"[+] Recebido pacote {seq_num}. Gravando no disco...")
            arquivo_destino.write(payload)
            seq_esperado += 1

            enviar_ack(sock, endereco_cliente, seq_num)

            if flag == 1:
                print('[*] Último pacote recebido. Transferência concluída.')
                arquivo_destino.close()
                break
        else:
            if seq_num < seq_esperado:
                enviar_ack(sock, endereco_cliente, seq_num)

except KeyboardInterrupt:
    print("\n[*] Servidor encerrado pelo usuário.")
    arquivo_destino.close()
