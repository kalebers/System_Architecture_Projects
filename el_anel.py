#!/usr/bin/env python3

#
# ASDPC
# Prof. Luiz Lima Jr.
#

import pika
import sys
from enum import Enum

Estados = Enum('Estados','INICIADOR INDECISO LIDERADO LIDER')

idx = None
Nx = []
estado = Estados.INDECISO
lider = None

canal = None

def espontaneamente(msg):
    print("espontaneamente", msg)
    muda_estado(Estados.INICIADOR)
    print("sou iniciador")
    envia(idx, Nx[0])

def recebendo(msg, origem):
    global lider
    print(f"Mensagem {msg} recebida de {origem}")
    if estado != Estados.LIDER:
        if msg < idx:
            temp = Nx[:]
            temp.remove(origem)
            envia(idx, temp[0])
        elif msg > idx:
            temp = Nx[:]
            temp.remove(origem)
            lider = msg
            envia(msg, temp[0])
            muda_estado(Estados.LIDERADO)
            print("serei liderado")
        else:
            muda_estado(Estados.LIDER)
            print("sou lider")
            lider = idx
            

def muda_estado(novo_estado):
    global estado
    estado = novo_estado

def envia(msg, para):
    m = f"{idx}:{msg}"
    print(f"Enviando {msg} para {para}")
    canal.basic_publish(exchange='', routing_key=para,
        body=m)

def alarme(p):
    pass


# callback
def callback(ch, method, props, body):
    msg = body.decode().split(":") # origem:msg
    if len(msg) < 2:
        print("erro no formato da msg")
        return
    origem = msg[0]
    m = msg[1]
    if origem.upper() == "NULL":
        espontaneamente(m)
    else: 
        recebendo(m, origem)


def main(meu_id, meus_vizinhos):
    global canal
    conexao = pika.BlockingConnection()     # conecta com broker
    canal = conexao.channel()               # canal para operações

    global idx, Nx
    idx = meu_id
    Nx = meus_vizinhos

    # cria fila
    canal.queue_declare(queue=idx, auto_delete=True)
    for v in Nx:
        canal.queue_declare(queue=v, auto_delete=True)

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
        print(f"USO: {sys.argv[0]} <idx> <v1> <v2> ...")
        exit(1) # erro
    else:
        main(sys.argv[1], sys.argv[2:])

