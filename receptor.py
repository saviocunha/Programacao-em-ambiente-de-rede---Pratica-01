
import socket
import struct
import os

# IP vazio ("") indica que o servidor irá escutar em todas as interfaces de rede disponíveis.
IP = ""

# Porta utilizada para receber os pacotes UDP.
PORTA = 8080

# Estrutura do cabeçalho:
# !  -> ordem de bytes em rede (big-endian)
# I  -> inteiro sem sinal de 4 bytes (número de sequência)
# I  -> inteiro sem sinal de 4 bytes (ID da transação)
# B  -> inteiro sem sinal de 1 byte (flag de controle)
FORMATO_CABECALHO = "!IIB"

# Calcula automaticamente o tamanho do cabeçalho em bytes.
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)


# Criação do socket UDP (AF_INET = IPv4, SOCK_DGRAM = UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Vincula o socket ao IP e Porta definidos
sock.bind((IP, PORTA))

print(f'[*] Servidor UDP aguardando arquivos em {IP} : {PORTA}...')

# Variáveis de controle de estado da transferência
seq_esperado = 0  # Próximo número de sequência que o servidor aceitará
arquivo_destino = open('arquivo.pdf', 'wb')  # Cria/abre o arquivo final em modo binário | w -> write (escrever) b -> binary (binário)
transacao_atual = None  # Guardará o ID da transferência ativa para evitar mistura de dados


try:
    while True:
        # Recebendo dados
        # Buffer de 2048 bytes é maior que o MTU padrão (1500), garantindo leitura do pacote cheio
        pacote, endereco_cliente = sock.recvfrom(2048)

        # Separa o cabeçalho dos dados reais (payload)
        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]

        # Desempacota o cabeçalho binário para variáveis do Python
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        # Se for o primeiro pacote da sessão, registramos o trans_id atual
        if transacao_atual is None:
            transacao_atual = trans_id

        # Verifica se o pacote pertence à transação atual
        if trans_id != transacao_atual:
            continue # Ignora pacotes de outras sessões/clientes "alienígenas"

        # Lógica de ordenação e ACK (Confirmação)
        if seq_num == seq_esperado:
            print(f"[+] Recebido pacote {seq_num}. Gravando no disco ...")
            arquivo_destino.write(payload)  # Grava o pedaço do arquivo no disco
            seq_esperado += 1  # Atualiza a sequência para o próximo bloco esperado

            # Criar e enviar o ACK correspondente ao pacote recebido com sucesso
            ack_pacote = struct.pack("!I", seq_num)
            sock.sendto(ack_pacote, endereco_cliente)

            # Verificar se a flag indica que este é o último pacote do arquivo
            if flag == 1:
                print('[*] Último pacote recebido. Transferência concluída.')
                arquivo_destino.close()  # Salva e fecha o arquivo com segurança
                break # Sai do loop de recebimento
        else:
            # Se o pacote for antigo/duplicado, o cliente pode ter perdido o nosso ACK anterior.
            # Reenviamos o ACK do pacote que o cliente mandou para tirá-lo do "limbo" de retransmissão.
            if seq_num < seq_esperado:
                ack_pacote = struct.pack("!I", seq_num)
                sock.sendto(ack_pacote, endereco_cliente)

except KeyboardInterrupt:
    # Captura o Ctrl+C no terminal para encerrar o servidor
    print("\n [*] Servidor encerrado pelo usuário.")
    arquivo_destino.close()  # Garante que o arquivo não fique corrompido ao fechar
