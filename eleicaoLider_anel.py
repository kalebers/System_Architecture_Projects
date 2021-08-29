#!/usr/bin/env python3

import pika
from sys import argv
from enum import Enum

Estados = Enum('Estados', 'INICIADOR OCIOSO LIDERADO LIDER')

idx = None
Nx = []
estado = Estados.OCIOSO
lider = None

canal = None

# EVENTOS

def espontaneamente(msg):
    print("Evento espontâneo:", msg)
    muda_estado(Estados.INICIADOR)
    print("Sou iniciador")
    envia(idx, [Nx[0]])
    
def recebendo(msg, origem):
    global lider
    print(f"Mensagem {msg} recebida de {origem}")
    if estado != Estados.LIDER:
        if msg == idx:
            # Se mensagem retornou para mim com meu indice, eu sou o líder
            muda_estado(Estados.LIDER)
            print("Sou lider")
            lider = idx
        else:
            # Caso contrário envia ao próximo nó o minimo entre seu proprio idx
            # e a msg recebida
            aux = Nx[:]
            aux.remove(origem)
            lider = min(idx, msg)
            envia(lider, [aux[0]])
            if lider != idx:
                # Se nao sou lider, altero estado para liderado
                muda_estado(Estados.LIDERADO)
                print("Sou Liderado")

def quando():
    print("Alarme disparou")

# Ações

def muda_estado(novo_estado):
    global estado
    estado = novo_estado

def envia(msg, para):
    m = f"{idx}:{msg}"
    print(f"Enviando {msg} para {para}")
    for d in para:
        canal.basic_publish(exchange='', routing_key=d, body=m)


# callback
def callback(ch, method, props, body):
    msg = body.decode().split(':') # ORIGEM:MSG  => ['ORIGEM', 'MSG' ]
    if len(msg) < 2:
        print("Erro formato da mensagem")
        return
    if msg[0].upper() == "NULL":
        espontaneamente(msg[1])
    else:
        recebendo(msg[1], msg[0])


def main(meu_id, meus_vizinhos):
    global canal
    conexao = pika.BlockingConnection()     # conecta com broker
    canal = conexao.channel()               # canal para operações

    global idx, Nx
    idx = meu_id
    Nx = meus_vizinhos

    # cria fila
    res = canal.queue_declare(queue=idx, auto_delete=True)
    for v in Nx:
        canal.queue_declare(queue=v, auto_delete=True)

    canal.basic_consume(queue=idx,
        on_message_callback=callback,
        auto_ack=True)

    try:
        print(f'{idx}: aguardando mensagens')
        canal.start_consuming()
    except KeyboardInterrupt:
        canal.stop_consuming()

    conexao.close()


if __name__ == '__main__':
    if len(argv) < 2:
        print(f"USO: {argv[0]} idx v1 v2 v3 ...")
        exit(1) # erro

    main(argv[1], argv[2:])

