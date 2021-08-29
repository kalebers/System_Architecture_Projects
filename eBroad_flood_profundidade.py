#!/usr/bin/env python3

#
# Implemetacao broadcast

import pika
import sys
from enum import Enum

Estados = Enum('Estados', 'INICIADOR OCIOSO VISITADO OK')

idx = None
Nx = []
nao_visitados = []
estado = Estados.OCIOSO
entrada = None 
iniciador = False

canal = None

def limpeza():
    global nao_visitados, estado, entrada, iniciador
    nao_visitados = []
    muda_estado(Estados.OCIOSO)
    entrada = None
    iniciador = False
    canal.queue_purge(queue = idx)
    for n in Nx:
        canal.queue_purge(queue = n)

def visita():
    if len(nao_visitados) != 0:
        prox = next(iter(nao_visitados))
        muda_estado(Estados.VISITADO)
        print(f" {idx}: Envia T para {prox}")
        envia('T', [prox])
    else:
        muda_estado(Estados.OK)
        if not iniciador:
            print(f" {idx}: Envia R para {entrada}")
            envia('R', [entrada])

# Eventos
def espontaneamente(msg):
    global nao_visitados, iniciador
    if msg.startswith('L'):
        print(f" {idx}: Limpando nó")
        limpeza()
        envia('L', Nx)
        return
    print(f" {idx}: INICIADOR")
    nao_visitados = Nx
    muda_estado(Estados.INICIADOR)
    iniciador = True 
    visita()

# ALGORITMO DISTRIBUIDO
def recebendo(msg, origem):
    global nao_visitados, iniciador, entrada
    #print(f" {idx}: Mensagem {msg} recebida de {origem}")
    if msg.startswith('L'):
        if estado != Estados.OCIOSO:
            print(f" {idx}: Limpando nó")
            limpeza()
            envia('L', Nx)
    elif estado == Estados.OCIOSO:
        print(f" {idx} OCIOSO: Mensagem {msg} recebida de {origem}")
        entrada = origem
        nao_visitados = set(Nx) - set([origem])
        iniciador = False
        visita()
    elif estado == Estados.VISITADO:
        print(f" {idx} VISITADO: Mensagem {msg} recebida de {origem}")
        nao_visitados = set(nao_visitados) - set([origem])
        if msg.startswith('T'):
            print(f" {idx}: Envia B para {origem}")
            envia('B', [origem])
        elif msg.startswith('R'):
            visita()
        elif msg.startswith('B'):
            visita()

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

