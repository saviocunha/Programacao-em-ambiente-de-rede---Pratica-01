# Importa os módulos necessários
import socket, struct, os, random

# Endereço IP do servidor de destino (neste caso, a propria máquina)
IP_DESTINO = "127.0.0.1"
# Define a porta de destino do servidor
PORTA_DESTINO = 8080

# Coloque um arquivo PDF real na mesma pasta
# altere o nome do arquivo de acordo com o código
# ou altere o código de acordo com o nome do arquivo 


# Nome do arquivo a ser enviado
NOME_ARQUIVO = "meu_arquivo.pdf"

# Tamanho máximo dos dados do arquivo por pacote (em bytes)
TAMANHO_PAYLOAD = 1024

# Formato do cabeçalho: ! (Big-Endian) + I (4 bytes para seq_num) + I (4 bytes para trans_id) + B (1 byte para flag)
FORMATO_CABECALHO = "!IIB"

# Cria o socket UDP (SOCK_DGRAM) para IPv4 (AF_INET)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definindo o Timeout. Se recvfrom demorar mais de 1 segundo,
# gera erro (exceção)
sock.settimeout(1.0)

# Gera um ID de transação aleatório para a sessão
trans_id = random.randint(1000, 9999)

# Inicializa o contador de pacotes enviados (começa em 0)
seq_num = 0

print(f'[*] Iniciando transferência de {NOME_ARQUIVO}')
print(f'[*] ID da transação: {trans_id}')



with open(NOME_ARQUIVO, 'rb') as arquivo: # Abre o arquivo em modo de leitura binária ('rb')
    while True:
        # Lê um pedaço do arquivo de até 1024 bytes
        pedaco = arquivo.read(TAMANHO_PAYLOAD)

        # Lógica para descobrir se é o último pacote
        # Define flag = 1 se for o último pedaço do arquivo ou se vier vazio; senão define flag = 0
        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD or not pedaco else 0

        if not pedaco and flag == 0: # Condição de segurança caso o arquivo termine sem dados residuais
            break # Encerra o loop de leitura
        

        # Cria o cabeçalho binário de 9 bytes
        cabecalho = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag)
        
        # Concatena o cabeçalho com o pedaço do arquivo
        pacote_completo = cabecalho + pedaco

        ack_recebido = False    # Flag para controlar se o ACK foi recebido
        tentativas = 0          # Inicializa o contador de retransmissões do pacote atual
        MAX_TENTATIVAS = 5      # Limite de tentativas antes de desistir


        # Loop do Stop-and-Wait (retransmissão)
        # Enquanto não receber o ACK e não estourar o limite de tentativas...
        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                # Enviar o pacote completo
                sock.sendto(pacote_completo, (IP_DESTINO, PORTA_DESTINO))
                print(f'[>] Pacote {seq_num} enviado. Aguardando ACK...(Tentativa {tentativas+1})')

                # Aguardar o ACK    
                ack_pacote, _ = sock.recvfrom(4)    # Espera 4 bytes (o strunct "!I")
                                                    # O código fica "travado" aqui até chegar algo ou dar timeout

                ack_num = struct.unpack('!I', ack_pacote) [0]   # Desempacota os 4 bytes para obter o número do ACK
                                                                # [0] Pega o primeiro elemento da tupla

                if ack_num == seq_num:      # Verifica se o número do ACK corresponde ao pacote enviado
                    print(f'[<] ACK {ack_num} recebido!')   
                    ack_recebido = True     # Altera para True para encerrar o loop de tentativas do pacote atual
                    seq_num += 1
                else:
                    print(f'[-] ACK incorreto recebido. Ignorando.')    # ACK de outro pacote (ex: atrasado/duplicado). Ignora e continua esperando.

            except socket.timeout:      # Se o tempo de espera (1s) acabar, assume-se que o pacote ou o ACK se perdeu
                print(f'[!] Timeout! Não recebi o ACK do pacote {seq_num}.')
                tentativas += 1         # Incrementa tentativas para reenviar o mesmo pacote
        

        # Verifica se o limite de retransmissões foi atingido
        if tentativas == MAX_TENTATIVAS:
            print('[-] Limite de retransmissões atingido. Conexão perdida.')
            break # Aborta a transferência

        
        # Verifica se a flag de fim de arquivo foi enviada e confirmada
        if flag == 1:
            print("[+] Transferência finalizada com sucesso.")
            break

