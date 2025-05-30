from http import HTTPStatus
from unittest.mock import MagicMock
from fastapi import HTTPException

# --- Testes para o CRUD de Residências ---


def test_cadastrar_residencia_success(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase

    mock_db.reset_mock()

    # Act
    response = client.post(
        f"/cidadao/cadastrar_residencias/{user_id}",
        json=residencia_payload,
    )

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["endereco"]["bairro"] == "Farol"
    assert data["coletavel"] is False
    assert "id" in data
    mock_db.collection().document().collection().document().set.assert_called_once()


def test_listar_residencias_success(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    """
    Testa a listagem de residências de um cidadão.
    """
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    _, mock_db, _ = mock_firebase

    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        "id": "residencia-1",
        **residencia_payload,
        "coletavel": False,
    }
    mock_doc2 = MagicMock()
    mock_doc2.to_dict.return_value = {
        "id": "residencia-2",
        **residencia_payload,
        "coletavel": True,
    }

    mock_db.collection().document().collection().stream.return_value = [
        mock_doc1,
        mock_doc2,
    ]

    # Act
    response = client.get(f"/cidadao/residencias/{user_id}")

    # Assert
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
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-a-editar"
    _, mock_db, _ = mock_firebase
    mock_db.collection().document().collection().document().get.return_value.exists = (
        True
    )

    mock_db.reset_mock()

    novo_payload = residencia_payload
    novo_payload["endereco"]["logradouro"] = "Rua do Comércio"

    # Act
    response = client.put(
        f"/cidadao/editar_residencias/{user_id}/{residencia_id}", json=novo_payload
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    # ... resto das asserções ...
    mock_db.collection().document().collection().document().set.assert_called_once()


def test_toggle_coleta_residencia(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    """
    Testa a mudança do status 'coletavel' de uma residência.
    """
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id = "residencia-toggle"
    _, mock_db, _ = mock_firebase
    mock_doc_ref = mock_db.collection().document().collection().document()

    initial_get = mock_doc_ref.get.return_value
    initial_get.exists = True
    initial_get.to_dict.return_value = {"coletavel": False}

    updated_get = MagicMock()
    updated_get.to_dict.return_value = {
        "id": residencia_id,
        **residencia_payload,
        "coletavel": True,
    }

    mock_doc_ref.get.side_effect = [initial_get, updated_get]

    # Act
    response = client.patch(f"/cidadao/residencias/{user_id}/{residencia_id}/coletar")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json()["coletavel"] is True
    mock_doc_ref.update.assert_called_with({"coletavel": True})


def test_listar_tutoriais(client, mock_firebase):
    # Arrange
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

    # Act
    response = client.get("/cidadao/tutoriais")

    # Assert
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["titulo"] == "Como separar o lixo"


# --- Testes de Falha para CRUD de Residências ---


def test_cadastrar_residencia_usuario_nao_encontrado(
    client, residencia_payload, mocker
):
    """
    Testa a falha ao tentar cadastrar residência para um usuário que não existe.
    """
    # Arrange
    user_id_invalido = "user-id-que-nao-existe"
    # Simula a falha na verificação do usuário
    mocker.patch(
        "routes.cidadao.verificar_usuario",
        side_effect=HTTPException(status_code=404, detail="Usuário não encontrado."),
    )

    # Act
    response = client.post(
        f"/cidadao/cadastrar_residencias/{user_id_invalido}", json=residencia_payload
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado."


def test_update_residencia_not_found(
    client, mock_firebase, created_cidadao, residencia_payload, mocker
):
    """
    Testa a falha ao tentar editar uma residência que não existe.
    """
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id_inexistente = "residencia-id-inexistente"
    _, mock_db, _ = mock_firebase

    # Simula o documento da residência não sendo encontrado
    mock_db.collection().document().collection().document().get.return_value.exists = (
        False
    )

    # Act
    response = client.put(
        f"/cidadao/editar_residencias/{user_id}/{residencia_id_inexistente}",
        json=residencia_payload,
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Residência não encontrada."


def test_coletar_residencia_not_found(client, mock_firebase, created_cidadao, mocker):
    """
    Testa a falha ao tentar marcar para coleta uma residência que não existe.
    """
    # Arrange
    mocker.patch("routes.cidadao.verificar_usuario")
    user_id = created_cidadao["uid"]
    residencia_id_inexistente = "residencia-id-inexistente"
    _, mock_db, _ = mock_firebase

    # Simula o documento da residência não sendo encontrado
    mock_db.collection().document().collection().document().get.return_value.exists = (
        False
    )

    # Act
    response = client.patch(
        f"/cidadao/residencias/{user_id}/{residencia_id_inexistente}/coletar"
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Residência não encontrada."
