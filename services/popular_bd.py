from firebase_config import db
def popular_bd_teste():
    usuarios = [
        {
            "nome_usuario": "João Silva",
            "email": "joao@email.com",
            "telefone": "+5511999999999",
            "role": "cidadao",
            "senha": "senha123",
            "cpf": "12345678909"
        },
        {
            "nome_usuario": "Cooperativa Central",
            "email": "contato@coopcentral.com",
            "telefone": "+5582999999999",
            "role": "cooperativa",
            "senha": "coop123",
            "cnpj": "12345678000100",
            "nome_cooperativa": "Coop Central",
            "area_atuacao": ["Centro", "Farol", "Ponta Verde"]
        },
        {
            "nome_usuario": "Carlos Motorista",
            "email": "carlos@motorista.com",
            "telefone": "+5571999999999",
            "role": "motorista",
            "senha": "motorista123",
            "cnh": "CNH12345678"
        }
    ]

    for usuario in usuarios:
        doc_ref = db.collection("usuarios").document()  # Gera ID automático
        doc_ref.set(usuario)

    print("Usuários populados com sucesso no Firestore!")

    cidadaos = [
        {
            "nome_usuario": "Ana Beatriz",
            "email": "ana.b@gmail.com",
            "telefone": "+5511988888888",
            "role": "cidadao",
            "senha": "senhaana123",
            "cpf": "98765432100"
        },
        {
            "nome_usuario": "Rafael Gomes",
            "email": "rafael.gomes@yahoo.com",
            "telefone": "+5511977777777",
            "role": "cidadao",
            "senha": "senharafael",
            "cpf": "11122233344"
        },
        {
            "nome_usuario": "Luciana Prado",
            "email": "luciana.prado@outlook.com",
            "telefone": "+5511966666666",
            "role": "cidadao",
            "senha": "luciana456",
            "cpf": "55544433322"
        },
        {
            "nome_usuario": "Tiago Ferreira",
            "email": "tiago.f@gmail.com",
            "telefone": "+5511955555555",
            "role": "cidadao",
            "senha": "tiagoSenha",
            "cpf": "44433322211"
        },
        {
            "nome_usuario": "Bruna Costa",
            "email": "bruna.costa@protonmail.com",
            "telefone": "+5511944444444",
            "role": "cidadao",
            "senha": "bruna789",
            "cpf": "22211100099"
        }
    ]
    for cidadao in cidadaos:
        db.collection("usuarios").add(cidadao)

    print("Inseriu cidadaos")

    cooperativas = [
        {
            "nome_usuario": "Cooperativa Esperança",
            "email": "contato@esperanca.com",
            "telefone": "+5582988888888",
            "role": "cooperativa",
            "senha": "esperanca123",
            "cnpj": "11122233000100",
            "nome_cooperativa": "Cooperativa Esperança",
            "area_atuacao": ["Benedito Bentes", "Tabuleiro"]
        },
        {
            "nome_usuario": "Cooperativa Verde Vida",
            "email": "contato@verdevida.com",
            "telefone": "+5582977777777",
            "role": "cooperativa",
            "senha": "verdevida456",
            "cnpj": "22233344000111",
            "nome_cooperativa": "Cooperativa Verde Vida",
            "area_atuacao": ["Jatiúca", "Ponta Verde"]
        }
    ]

    # Adiciona no Firestore e guarda os IDs
    coop_ids = []
    for coop in cooperativas:
        ref = db.collection("usuarios").add(coop)
        coop_ids.append(ref[1].id)

    motoristas = [
        # Motoristas da Cooperativa Esperança
        {
            "nome": "Marcos Lima",
            "telefone": "+5582911111111",
            "email": "marcos.lima@esperanca.com",
            "senha": "marcos123",
            "coop_id": coop_ids[0],
            "bairro": ["Benedito Bentes"]
        },
        {
            "nome": "Patrícia Nogueira",
            "telefone": "+5582922222222",
            "email": "patricia.n@esperanca.com",
            "senha": "patricia456",
            "coop_id": coop_ids[0],
            "bairro": ["Tabuleiro"]
        },
        # Motoristas da Cooperativa Verde Vida
        {
            "nome": "Eduardo Souza",
            "telefone": "+5582933333333",
            "email": "eduardo.s@verdevida.com",
            "senha": "eduardo789",
            "coop_id": coop_ids[1],
            "bairro": ["Jatiúca"]
        },
        {
            "nome": "Fernanda Alves",
            "telefone": "+5582944444444",
            "email": "fernanda.a@verdevida.com",
            "senha": "fernanda321",
            "coop_id": coop_ids[1],
            "bairro": ["Ponta Verde"]
        }
    ]

    # Adiciona ao Firestore
    for motorista in motoristas:
        motorista["em_rota"] = False
        db.collection("motoristas").add(motorista)
    print("ok")

