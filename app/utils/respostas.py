from flask import jsonify


def resposta_erro(mensagem, status=400):
    return jsonify({
        "sucesso": False,
        "mensagem": mensagem
    }), status


def resposta_sucesso(mensagem, dados=None, status=200):
    resposta = {
        "sucesso": True,
        "mensagem": mensagem
    }

    if dados is not None:
        resposta["dados"] = dados

    return jsonify(resposta), status
