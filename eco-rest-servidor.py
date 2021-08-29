# Kalebe Rodrigues Szlachta
# usar porta 1588

from flask import Flask, request 
from flask_restful import Resource, Api

ap = Flask(__name__)
api = Api(ap)

# faz referencia a SIB (soup) = implementação
class Conta:
    def __init__(self, id:str):
        self.id = id
        self.saldo = 0

    def deposito(self, depos:float):
        self.saldo += depos
        return self.saldo

    def saque(self, saqu:float):
        self.saldo -= saqu
        return self.saldo

conta = Conta("1234-5")


# api
class ContaApi(Resource):
    def get(self, id):
        return {'Cont': conta.saldo}

    def patch(self, id, operacao):
        if (operacao == "deposito"):
            valor = float(request.form.get('valor'))
            return {'Resp': conta.deposito(valor)}
        elif (operacao == "saque"):
            valor = float(request.form.get('valor'))
            return {'Resp': conta.saque(valor)}
        return {"Resp": "Funcao nao existe" }



api.add_resource(ContaApi, '/contas/<string:id>', '/contas/<string:id>/<string:operacao>')

if __name__ == '__main__':
    ap.env = 'development'
    ap.run(port=1588, debug=True)

