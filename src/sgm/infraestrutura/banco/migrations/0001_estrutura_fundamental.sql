PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS versoes_banco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_migracao TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    aplicada_em TEXT NOT NULL,
    versao_sistema TEXT NOT NULL,
    checksum TEXT NOT NULL,
    resultado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (
        perfil IN ('ADMINISTRADOR','RESPONSAVEL_TECNICO','ANALISTA','AUDITOR','CONSULTA')
    ),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    bloqueado_ate TEXT,
    ultimo_acesso TEXT,
    criado_em TEXT NOT NULL,
    alterado_em TEXT NOT NULL,
    versao INTEGER NOT NULL DEFAULT 1,
    excluido_em TEXT
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo_pessoa TEXT NOT NULL CHECK (tipo_pessoa IN ('FISICA', 'JURIDICA')),
    documento TEXT,
    email TEXT,
    telefone TEXT,
    observacoes TEXT,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL,
    alterado_em TEXT NOT NULL,
    criado_por_id INTEGER,
    alterado_por_id INTEGER,
    versao INTEGER NOT NULL DEFAULT 1,
    excluido_em TEXT,
    FOREIGN KEY (criado_por_id) REFERENCES usuarios(id),
    FOREIGN KEY (alterado_por_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS processos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificador_interno TEXT NOT NULL UNIQUE,
    numero_processo_informado TEXT,
    numero_processo_normalizado TEXT,
    numero_processo_valido INTEGER CHECK (numero_processo_valido IN (0, 1)),
    cliente_id INTEGER NOT NULL,
    tribunal TEXT NOT NULL,
    vara TEXT,
    municipio TEXT,
    fase_processual TEXT NOT NULL,
    tipo_trabalho TEXT NOT NULL,
    status TEXT NOT NULL,
    data_recebimento TEXT NOT NULL,
    prazo TEXT,
    data_base_atual TEXT,
    observacoes TEXT,
    ambiente_origem TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    alterado_em TEXT NOT NULL,
    criado_por_id INTEGER NOT NULL,
    alterado_por_id INTEGER NOT NULL,
    versao INTEGER NOT NULL DEFAULT 1,
    excluido_em TEXT,
    motivo_exclusao TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (criado_por_id) REFERENCES usuarios(id),
    FOREIGN KEY (alterado_por_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS eventos_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER,
    usuario_id INTEGER,
    evento TEXT NOT NULL,
    categoria TEXT NOT NULL,
    entidade TEXT,
    entidade_id INTEGER,
    valor_anterior TEXT,
    valor_posterior TEXT,
    data_hora TEXT NOT NULL,
    versao_sistema TEXT NOT NULL,
    ambiente TEXT NOT NULL,
    estacao TEXT NOT NULL,
    resultado TEXT NOT NULL,
    detalhes TEXT,
    FOREIGN KEY (processo_id) REFERENCES processos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificador TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    ambiente TEXT NOT NULL,
    caminho_destino TEXT NOT NULL,
    iniciado_em TEXT NOT NULL,
    concluido_em TEXT,
    tamanho_bytes INTEGER,
    hash_manifesto TEXT,
    resultado TEXT NOT NULL,
    verificado INTEGER NOT NULL DEFAULT 0 CHECK (verificado IN (0, 1)),
    restauracao_testada INTEGER NOT NULL DEFAULT 0 CHECK (restauracao_testada IN (0, 1)),
    responsavel_id INTEGER,
    observacoes TEXT,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_processos_numero_normalizado
    ON processos(numero_processo_normalizado);
CREATE INDEX IF NOT EXISTS idx_processos_cliente
    ON processos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_processos_status
    ON processos(status);
CREATE INDEX IF NOT EXISTS idx_processos_prazo
    ON processos(prazo);
CREATE INDEX IF NOT EXISTS idx_eventos_auditoria_processo
    ON eventos_auditoria(processo_id);
