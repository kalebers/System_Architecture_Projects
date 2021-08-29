#!/usr/bin/env python3

#
# Implemetacao broadcast

import pika
import sys
from enum import Enum

Estados = Enum('Estados', 'INCIADOR OCIOSO OK')

idx = None
Nx = []
estado = Estados.OCIOSO

canal = None

# Eventos
def espontaneamente(msg):
    print("Espontaneamente", msg)
    muda_estado(Estados.INCIADOR)
    print("Sou o iniciador")
    muda_estado(Estados.OK)
    envia(msg, Nx)

# ALGORITMO DISTRIBUIDO
def recebendo(msg, origem):
    # passar idx para flood e tirar o Nx
    print(f" {idx}: Mensagem {msg} recebida de {origem}")
    if estado == Estados.OCIOSO:
        muda_estado(Estados.OK)
        envia(msg, set(Nx) - set(origem))

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

