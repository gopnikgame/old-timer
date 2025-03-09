-- Таблица karma
CREATE TABLE IF NOT EXISTS karma (
    user_id BIGINT PRIMARY KEY,
    karma INT NOT NULL DEFAULT 0
);

-- Таблица predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    prediction_text TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() at time zone 'utc')
);

-- Таблица predictions_archive
CREATE TABLE IF NOT EXISTS predictions_archive (
    user_id BIGINT NOT NULL,
    prediction_text TEXT NOT NULL
);

-- Таблица karma_updates
CREATE TABLE IF NOT EXISTS karma_updates (
    user_id BIGINT NOT NULL,
    karma INT NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL
);