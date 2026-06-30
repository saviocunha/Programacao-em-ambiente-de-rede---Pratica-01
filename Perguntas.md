# Perguntas

#### 4.1 - Qual é o tamanho máximo seguro que um pacote UDP pode ter para transitar pela internet (ou seja, fora de rede local) sem sofrer fragmentação? Por que isso é necessário? Como isso afeta o tamanho dos pedaços do arquivo que você vai ler por vez no seu código?
O tamanho máximo seguro para um pacote UDP transitar pela internet sem sofrer fragmentação é de 1472 bytes para IPv4 (ou 1452 bytes para IPv6). Isso ocorre porque o limite padrão da rede (MTU) na internet é de \(1500\) bytes, e os cabeçalhos de rede consomem o restante. No código, para ler um arquivo e transmiti-lo de forma eficiente via UDP sem fragmentação, você deve configurar o tamanho do "buffer" (o pedaço do arquivo lido por vez) para caber exatamente no payload seguro.

#### 4.2 - O que é o conceito de Stop-and-Wait? Desenhe um diagrama de sequência de como o cliente e o servidor conversam nesse modelo se um pacote for perdido.
É um protocolo fundamental de controle de fluxo e erro. O emissor envia exatamente um pacote de dados e obrigatoriamente para, aguardando uma confirmação (ACK) do receptor antes de enviar o próximo. Se o pacote for perdido, um temporizador (timeout) expira e o emissor reenvia o mesmo pacote.

``` mermaid 
sequenceDiagram
    participant C as Cliente (Emissor)
    participant S as Servidor (Receptor)

    Note over C,S: Stop-and-Wait - Perda de Pacote

    C->>S: Pacote (Seq=0)
    Note right of S: ❌ Pacote perdido

    Note over C: Inicia temporizador
    Note over C: Timeout

    C->>S: Retransmite Pacote (Seq=0)

    activate S
    S-->>C: ACK(0)
    deactivate S

    C->>S: Pacote (Seq=1)

    activate S
    S-->>C: ACK(1)
    deactivate S
```

#### 4.3 - Em redes de computadores, qual é a ordem de bytes padrão para transmissão na rede (Network Byte Order)? É Big-Endian ou Little-Endian?
A ordem de bytes padrão para transmissão em redes (Network Byte Order) é Big-Endian.I sso significa que o byte mais significativo (o de maior valor) é sempre transmitido primeiro na rede, independentemente da arquitetura do processador local (que pode ser Little-Endian, comum em chips x86/ARM). 



#### 5.1 Quais são as situações em que é melhor usar codificação base64 ou usar struct.pack?

A escolha entre codificação Base64 e struct.pack depende de os dados precisarem ser transportados de forma segura como texto ou compactados como binário cru.
Use base64 quando precisar converter dados binários em caracteres ASCII imprimíveis para enviá-los através de canais que corrompem ou não suportam bytes brutos (como e-mails, JSON ou URLs).
Use struct.pack para serializar múltiplos tipos de dados Python (inteiros, floats, etc.) diretamente em uma sequência de bytes brutos formatados, seguindo uma estrutura de layout definida.


#### 8.1 Será possivel testar através da internet? Explique.

