
-- ===========================
-- Tabela COLABORADOR
-- ===========================
CREATE TABLE IF NOT EXISTS colaborador (
    id_colab        INTEGER PRIMARY KEY AUTOINCREMENT,
    nm_colaborador  TEXT NOT NULL,
    area            TEXT,
    papel           TEXT,
    consentimento_privacidade INTEGER DEFAULT 1,
    ativo           INTEGER DEFAULT 1
);

-- ===========================
-- Tabela CHECKIN
-- ===========================
CREATE TABLE IF NOT EXISTS checkin (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_colab        INTEGER NOT NULL,
    dt              TEXT NOT NULL,
    q1              INTEGER NOT NULL,
    q2              INTEGER NOT NULL,
    q3              INTEGER NOT NULL,
    q4              INTEGER NOT NULL,
    q5              INTEGER NOT NULL,
    texto_opcional  TEXT,
    FOREIGN KEY (id_colab) REFERENCES colaborador(id_colab)
);

-- ===========================
-- Tabela ENERGIA
-- ===========================
CREATE TABLE IF NOT EXISTS energia (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    dt          TEXT NOT NULL,
    kwh         REAL NOT NULL,
    equipamento TEXT,
    local       TEXT,
    cd_area     INTEGER
);

-- ===========================
-- Tabela INCLUSAO_RECRUT
-- ===========================
CREATE TABLE IF NOT EXISTS inclusao_recrut (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_ref   TEXT NOT NULL,
    aprovado    INTEGER NOT NULL,
    score       REAL
);
PRAGMA foreign_keys = ON;