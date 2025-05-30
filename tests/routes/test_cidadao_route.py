import pytest
from http import HTTPStatus
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import date

# --- Testes para o CRUD de Residências ---


def test_cadastrar_residencia_success(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase
    mock_db.reset_mock()

    response = client.post(
        f"/cidadao/cadastrar_residencias/{user_id}", json=residencia_payload
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert "id" in data
    assert data["endereco"]["bairro"] == "Farol"
    mock_db.collection().document().collection().document().set.assert_called_once()


def test_listar_residencias_success(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase
    mock_doc1 = MagicMock(
        to_dict=MagicMock(
            return_value={"id": "res-1", "coletavel": False, **residencia_payload}
        )
    )
    mock_doc2 = MagicMock(
        to_dict=MagicMock(
            return_value={"id": "res-2", "coletavel": True, **residencia_payload}
        )
    )
    mock_db.collection().document().collection().stream.return_value = [
        mock_doc1,
        mock_doc2,
    ]

    response = client.get(f"/cidadao/residencias/{user_id}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2
    assert data[1]["coletavel"] is True


def test_deletar_residencia_success(client, mock_firebase, created_cidadao, mocker):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-a-deletar"
    _, mock_db, _ = mock_firebase
    mock_doc_ref = mock_db.collection().document().collection().document()
    mock_doc_ref.get.return_value.exists = True

    response = client.delete(f"/cidadao/deletar_residencias/{user_id}/{residencia_id}")

    assert response.status_code == HTTPStatus.NO_CONTENT
    mock_doc_ref.delete.assert_called_once()


def test_update_residencia_success(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-a-editar"
    _, mock_db, _ = mock_firebase
    mock_db.collection().document().collection().document().get.return_value.exists = (
        True
    )
    mock_db.reset_mock()
    novo_payload = residencia_payload.copy()
    novo_payload["endereco"]["logradouro"] = "Rua do Comércio"

    response = client.put(
        f"/cidadao/editar_residencias/{user_id}/{residencia_id}", json=novo_payload
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["endereco"]["logradouro"] == "Rua do Comércio"
    mock_db.collection().document().collection().document().set.assert_called_once()


def test_toggle_coleta_residencia(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-toggle"
    _, mock_db, _ = mock_firebase
    mock_doc_ref = mock_db.collection().document().collection().document()
    initial_get = MagicMock(exists=True)
    initial_get.to_dict.return_value = {"coletavel": False}
    updated_get = MagicMock(
        to_dict=MagicMock(
            return_value={"id": residencia_id, "coletavel": True, **residencia_payload}
        )
    )
    mock_doc_ref.get.side_effect = [initial_get, updated_get]

    response = client.patch(f"/cidadao/residencias/{user_id}/{residencia_id}/coletar")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["coletavel"] is True
    mock_doc_ref.update.assert_called_with({"coletavel": True})


# --- Teste de Falha Parametrizado: Residência Não Encontrada ---


@pytest.mark.parametrize(
    "http_method, url_path",
    [
        ("delete", "/cidadao/deletar_residencias/{user_id}/{residencia_id}"),
        ("put", "/cidadao/editar_residencias/{user_id}/{residencia_id}"),
        ("patch", "/cidadao/residencias/{user_id}/{residencia_id}/coletar"),
    ],
)
def test_residencia_actions_not_found(
    client,
    mock_firebase,
    created_cidadao,
    residencia_payload,
    mocker,
    http_method,
    url_path,
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-inexistente"
    _, mock_db, _ = mock_firebase
    mock_db.collection().document().collection().document().get.return_value.exists = (
        False
    )

    url = url_path.format(user_id=user_id, residencia_id=residencia_id)
    method_to_call = getattr(client, http_method)

    kwargs = {}
    if http_method == "put":
        kwargs["json"] = residencia_payload

    response = method_to_call(url, **kwargs)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "Residência não encontrada" in response.json()["detail"]


# --- Teste de Falha Parametrizado: Usuário Inválido ---


@pytest.mark.parametrize(
    "http_method, url_path",
    [
        ("post", "/cidadao/cadastrar_residencias/{user_id}"),
        ("get", "/cidadao/residencias/{user_id}"),
        ("delete", "/cidadao/deletar_residencias/{user_id}/res-1"),
        ("put", "/cidadao/editar_residencias/{user_id}/res-1"),
        ("patch", "/cidadao/residencias/{user_id}/res-1/coletar"),
    ],
)
def test_user_not_found_on_all_endpoints(
    client, residencia_payload, mocker, http_method, url_path
):
    user_id_invalido = "user-invalido"
    mocker.patch(
        "routes.cidadao.verificar_usuario",
        side_effect=HTTPException(status_code=404, detail="Usuário não encontrado."),
    )

    url = url_path.format(user_id=user_id_invalido)
    method_to_call = getattr(client, http_method)

    kwargs = {}
    if http_method in ["post", "put"]:
        kwargs["json"] = residencia_payload

    response = method_to_call(url, **kwargs)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "Usuário não encontrado" in response.json()["detail"]


# --- Testes para a Rota /ver_mapa ---


def test_ver_mapa_success(client, mock_firebase, created_cidadao, mocker):
    mocker.patch("routes.cidadao.verificar_usuario")
    mocker.patch("routes.cidadao.gerar_mapa_com_coops", return_value="mapa-gerado-url")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase

    # Mock de residência do usuário
    mock_residencia = MagicMock(
        to_dict=MagicMock(return_value={"endereco": {"bairro": "jatiúca"}})
    )
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]

    # Mock de cooperativa que atende o bairro
    mock_cooperativa = MagicMock(
        to_dict=MagicMock(
            return_value={"role": "cooperativa", "bairros_atendidos": ["jatiúca"]}
        )
    )
    mock_db.collection("usuarios").stream.return_value = [mock_cooperativa]

    response = client.get(f"/cidadao/ver_mapa/{user_id}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data["cooperativas"]) == 1
    assert data["mapa"] == "mapa-gerado-url"


def test_ver_mapa_no_cooperativas_na_regiao(
    client, mock_firebase, created_cidadao, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase
    mock_residencia = MagicMock(
        to_dict=MagicMock(return_value={"endereco": {"bairro": "jatiúca"}})
    )
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]
    mock_cooperativa = MagicMock(
        to_dict=MagicMock(
            return_value={"role": "cooperativa", "bairros_atendidos": ["ponta verde"]}
        )
    )
    mock_db.collection("usuarios").stream.return_value = [mock_cooperativa]

    response = client.get(f"/cidadao/ver_mapa/{user_id}")

    assert response.status_code == HTTPStatus.OK
    assert "Nenhuma cooperativa atende sua região" in response.json()["message"]


# --- Testes para a Rota /ver_rota ---


def test_ver_rota_success(client, mock_firebase, created_cidadao, mocker):
    mocker.patch("routes.cidadao.verificar_usuario")
    mocker.patch("routes.cidadao.gerar_rota_no_mapa", return_value="rota-visual-url")

    mock_date = mocker.patch("routes.cidadao.date")
    mock_date.today.return_value = date(2025, 5, 30)

    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase

    # Mock das residências do usuário
    mock_residencia = MagicMock(id="res-123")
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]

    # Mock de uma rota ativa que inclui a residência do usuário
    mock_rota = MagicMock(to_dict=MagicMock(return_value={"residencias": ["res-123"]}))

    mock_query_ref = mock_db.collection("rotas").where.return_value
    mock_query_ref.stream.return_value = [mock_rota]

    response = client.get(f"/cidadao/ver_rota/{user_id}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data["rotas"]) == 1
    assert data["rota_visual"] == "rota-visual-url"


def test_ver_rota_no_rota_ativa(client, mock_firebase, created_cidadao, mocker):
    mocker.patch("routes.cidadao.verificar_usuario")

    mock_date = mocker.patch("routes.cidadao.date")
    mock_date.today.return_value = date(2025, 5, 30)

    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase
    mock_residencia = MagicMock(id="res-123")
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]

    mock_query_ref = mock_db.collection("rotas").where.return_value
    mock_query_ref.stream.return_value = []  # Nenhuma rota hoje

    response = client.get(f"/cidadao/ver_rota/{user_id}")

    assert response.status_code == HTTPStatus.OK
    assert (
        "Nenhuma residência do usuário está em rota ativa hoje"
        in response.json()["message"]
    )


# --- Testes para a Rota /feedback ---


def test_enviar_feedback_success(client, mock_firebase, created_cidadao, mocker):
    mocker.patch("routes.cidadao.verificar_usuario")

    mock_date = mocker.patch("routes.cidadao.date")
    mock_date.today.return_value = date(2025, 5, 30)

    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase

    # Mock das residências e rota ativa
    mock_residencia = MagicMock(id="res-123")
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]
    mock_rota = MagicMock(to_dict=MagicMock(return_value={"residencias": ["res-123"]}))

    mock_query_ref = mock_db.collection("rotas").where.return_value
    mock_query_ref.stream.return_value = [mock_rota]

    feedback_payload = {"nota": 5, "comentario": "Excelente!"}
    response = client.post(f"/cidadao/feedback/{user_id}", json=feedback_payload)

    assert response.status_code == HTTPStatus.CREATED
    assert "Feedback enviado com sucesso" in response.json()["message"]
    mock_db.collection("feedback_coletas").add.assert_called_once()


def test_enviar_feedback_no_active_route(
    client, mock_firebase, created_cidadao, mocker
):
    mocker.patch("routes.cidadao.verificar_usuario")

    mock_date = mocker.patch("routes.cidadao.date")
    mock_date.today.return_value = date(2025, 5, 30)

    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase
    mock_residencia = MagicMock(id="res-123")
    mock_db.collection().document().collection().stream.return_value = [mock_residencia]

    mock_query_ref = mock_db.collection("rotas").where.return_value
    mock_query_ref.stream.return_value = []  # Nenhuma rota

    feedback_payload = {"nota": 5, "comentario": "Nao vieram"}
    response = client.post(f"/cidadao/feedback/{user_id}", json=feedback_payload)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Nenhuma coleta registrada hoje" in response.json()["detail"]


# --- Testes para a Rota /tutoriais ---


def test_listar_tutoriais(client, mock_firebase):
    _, mock_db, _ = mock_firebase
    mock_tutoriais = [
        MagicMock(
            to_dict=MagicMock(
                return_value={
                    "id": "tut-1",
                    "titulo": "Como separar o lixo",
                    "conteudo": "...",
                }
            )
        ),
        MagicMock(
            to_dict=MagicMock(
                return_value={
                    "id": "tut-2",
                    "titulo": "Tipos de Plástico",
                    "conteudo": "...",
                }
            )
        ),
    ]
    mock_db.collection("tutoriais").stream.return_value = mock_tutoriais

    response = client.get("/cidadao/tutoriais")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["titulo"] == "Como separar o lixo"
