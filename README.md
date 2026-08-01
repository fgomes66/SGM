# Sistema Método Gomes — MVP 0.1.0

## Instalação no Windows

```bat
cd C:\caminho\sgm_mvp_0_1_0
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Inicializar o banco

```bat
python scripts\inicializar_banco.py
```

## Criar o administrador

```bat
python scripts\criar_usuario.py
```

## Verificar a integridade

```bat
python scripts\verificar_integridade.py
```

## Executar os testes

```bat
pytest -v
```

O banco é criado em `dados/sgm_desenvolvimento.db`.
