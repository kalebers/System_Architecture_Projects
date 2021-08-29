#Kalebe Rodrigues Szlachta
#!/usr/bin/env python3

#
# Implemetacao broadcast

import pika
import sys
from enum import Enum

Estados = Enum('Estados', 'INICIADOR OCIOSO SCAN OK')
# OCIOSO - não recebeu nenhum R
# SCAN - já recebeu pelo menos um R e está esperando 
#        receber Rs ou Is de todos os vizinhos


idx = None
Nx = []
entrada = None
remetentes = []
info = []

estado = Estados.OCIOSO

canal = None

# Eventos
def espontaneamente(msg):
    print("Iniciando Eco/Waves", msg)
    muda_estado(Estados.INICIADOR)
    #muda_estado(Estados.OK)
    envia(msg, Nx)

def limpeza():
    global remetentes, entrada, info
    remetentes = []
    entrada = None
    info = []
    muda_estado(Estados.OCIOSO)

# ALGORITMO DISTRIBUIDO
def recebendo(msg, origem):
    global remetentes, entrada, info
    
    # TRIAGEM
    # Faz a leitura inicial por tipo de mensagem
    # - Se for do tipo I (info) armazena as informações
    # - Se for do tipo L (limpeza) reseta os dados 
    #   (usado apenas após o iniciador receber todas as informações) 
    # - Se for do tipo R, na primeira vez recebida armazena a entrada
    #   e envia R para os vizinhos (exceto entrada)
    if msg.startswith('I'):
        print(f" {idx}: Mensagem {msg} recebida de {origem}")
        remetentes.append(origem)
        info.extend(msg.split('-')[1].split(','))
    elif msg.startswith('L') and estado == Estados.OK:
        limpeza()
        envia('L', Nx)
    elif msg.startswith('R'):
        remetentes.append(origem)
        if estado == Estados.OCIOSO:
            print(f" {idx}: Mensagem {msg} recebida de {origem}")
            entrada = origem
            muda_estado(Estados.SCAN)
            envia(msg, set(Nx) - set([entrada]))

    # Tanto para I ou R recebidos, após o nó passar pela triagem
    # quando todos os vizinhos tiverem mandado um I ou R o nó
    # irá enviar as informações armazenadas para a nó de entrada
    if msg.startswith('I') or msg.startswith('R'):
        if estado == Estados.SCAN:
            if (set(Nx) - set(remetentes) == set()):
                msg = "I-"
                for i in info:
                    msg += "{},".format(i)
                msg += "{}".format(idx)
                envia(msg, [entrada])
                muda_estado(Estados.OK)

    # Quando o iniciador tiver recebido informações de todos
    # os vizinhos (Nx is subset of info?) então mostra todas
    # as informações recebidas e requisita a limpeza da rede
    if estado == Estados.INICIADOR:
        if (set(Nx).issubset(set(info))):
            info.append(idx)
            print( "Rede: ", set(info) )
            envia("L", Nx)
            limpeza()

def quando():
    print("Alarme!")

# Acoes
def muda_estado(novo_estado):
    global estado
    estado = novo_estado

def envia(msg, para):
    # ORIGEM: MSG
    m = f"{idx}:{msg}"
    for d in para:
        canal.basic_publish(exchange = '', routing_key = d, body = m)

def alarme(p):
    pass

# callback
def callback(ch, method, props, body):
    msg = body.decode().split(':') #ORIGEM:MSG
    if len(msg) < 2:
        print("Erro no formato da msg")
        return 
    origem = msg[0]
    m = msg[1]
    if origem.upper() == "NULL":
        espontaneamente(m)
    else:
        recebendo(m, origem)
    #recebe(msg[1], msg[0], ch) 


def main(meu_id, meus_vizinhos):
    global canal
    conexao = pika.BlockingConnection()     # conecta com broker
    canal = conexao.channel()               # canal para operações
    
    global idx, Nx

    idx = meu_id
    Nx = meus_vizinhos

    # cria fila 
    canal.queue_declare(queue = idx, auto_delete = True)
    for v in Nx:
        canal.queue_declare(queue = v, auto_delete = True)

    canal.basic_consume(queue=idx,
        on_message_callback=callback,
        auto_ack=True)

    try:
        print(f'{idx}: Aguardando mensagens')
        canal.start_consuming()
    except KeyboardInterrupt:
        canal.stop_consuming()

    conexao.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"USO: {sys.argv[0]} idx v1 v2 v3 ....")
        exit(1) # erro
    else:
        main(sys.argv[1], sys.argv[2:])

