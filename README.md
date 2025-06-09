# Rota Verde — Back-end

🚀 Backend da plataforma **Rota Verde**, que conecta cidadãos, cooperativas e motoristas para otimizar a coleta seletiva de resíduos.

📍 **Deploy (Swagger UI):** [https://rota-verde-back.onrender.com/docs](https://rota-verde-back.onrender.com/docs)

⭐️ **Repositório público:** [https://github.com/rota-verde/back-end](https://github.com/rota-verde/back-end)

---

### Componentes

✅ **Usuários Finais**  
- Cidadão  
- Cooperativa  
- Motorista  

✅ **Frontend (Mobile App)**  
- Em desenvolvimento (React Native)  
- Consome a API RESTful exposta pelo backend

✅ **Backend (FastAPI)**  
- Estrutura modular com:
  - `models/` → modelagem de dados  
  - `routes/` → endpoints RESTful  
  - `schemas/` → validação com Pydantic  
  - `services/` → lógica de negócio  
  - `tests/` → cobertura de testes unitários e de integração
- Integração com Firebase (`firebase_config.py`)

✅ **Firebase Services (Google)**  
- Authentication  
- Storage / Firestore 

✅ **Deploy**  
- Plataforma Render.com com CI/CD

---

## 📚 Principais endpoints

### /auth
- Cadastro, login, recuperação e deleção de usuários

### /cidadao
- Gestão de residências
- Visualização de rotas e mapa
- Feedback e tutoriais

### /cooperativa
- Gestão de motoristas
- Criação e gestão de rotas
- Gestão de bairros e materiais recicláveis

### /motorista
- Gestão das rotas do dia
- Início e finalização de rotas em tempo real

---

## 🧪 Testes
- Framework: **pytest**
- Cobertura de testes configurada (`.coveragerc`, `pytest.ini`)
- Testes localizados em `tests/`

---

## 🌱 Contribua

Quer contribuir com o Rota Verde?  
Abra uma issue ou envie um pull request!  
Juntos podemos tornar a coleta seletiva mais eficiente, transparente e participativa. ♻️

---

#RotaVerde #FastAPI #OpenSource #CleanTech #BackendDevelopment #APIs #Python #Firebase #ColetaSeletiva
