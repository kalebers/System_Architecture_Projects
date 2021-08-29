from flask import Flask, request
from flask_restful import Resource, Api

ap = Flask(__name__)
api = Api(ap)


# SIB = implementação

class Conta:
    def __init__(self, id:str):
        self.id = id
        self.saldo = 0

    def deposito(self, dep:float):
        self.saldo += dep
        return self.saldo

conta = Conta("12345")

# api
class ContaApi(Resource):
    def get(self, id):
        return {"cont":conta.saldo}
    
    def patch(self, id):
        valor = float(request.args.get("valor"))
        return {"resp":conta.deposito(valor)}


api.add_resource(ContaApi, '/contas/<string:id>', '/contas/<string:id>/deposito')

if __name__ == "__main__":
    ap.env = 'development'
    ap.run(port=1621, debug = True)