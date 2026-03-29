-- Complex financial schema for Track B deployment on PostgreSQL

CREATE TABLE IF NOT EXISTS instruments (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL UNIQUE,
    exchange VARCHAR(16) NOT NULL,
    asset_class VARCHAR(32) NOT NULL,
    currency VARCHAR(8) NOT NULL,
    sector VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_ticks (
    id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    tick_ts TIMESTAMPTZ NOT NULL,
    open NUMERIC(20,6),
    high NUMERIC(20,6),
    low NUMERIC(20,6),
    close NUMERIC(20,6),
    volume BIGINT,
    source VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(instrument_id, tick_ts, source)
);

CREATE INDEX IF NOT EXISTS idx_market_ticks_instrument_ts ON market_ticks(instrument_id, tick_ts DESC);

CREATE TABLE IF NOT EXISTS fundamentals (
    id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    as_of_date DATE NOT NULL,
    pe_ratio NUMERIC(20,6),
    debt_to_equity NUMERIC(20,6),
    revenue_growth NUMERIC(20,6),
    earnings_growth NUMERIC(20,6),
    return_on_equity NUMERIC(20,6),
    market_cap NUMERIC(24,2),
    source VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(instrument_id, as_of_date, source)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id BIGSERIAL PRIMARY KEY,
    owner_name VARCHAR(128) NOT NULL,
    base_currency VARCHAR(8) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
    id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id),
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    quantity NUMERIC(20,6) NOT NULL,
    average_cost NUMERIC(20,6) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(portfolio_id, instrument_id)
);

CREATE TABLE IF NOT EXISTS watchlists (
    id BIGSERIAL PRIMARY KEY,
    owner_name VARCHAR(128) NOT NULL,
    list_name VARCHAR(64) NOT NULL,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(owner_name, list_name, instrument_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    owner_name VARCHAR(128) NOT NULL,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    rule_type VARCHAR(32) NOT NULL,
    threshold NUMERIC(20,6) NOT NULL,
    direction VARCHAR(16) NOT NULL,
    channel VARCHAR(32) NOT NULL DEFAULT 'in_app',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alert_events (
    id BIGSERIAL PRIMARY KEY,
    alert_id BIGINT NOT NULL REFERENCES alerts(id),
    triggered_at TIMESTAMPTZ NOT NULL,
    observed_value NUMERIC(20,6) NOT NULL,
    context JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS api_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(64) NOT NULL,
    endpoint TEXT NOT NULL,
    symbol VARCHAR(32),
    success BOOLEAN NOT NULL,
    error_message TEXT,
    latency_ms INTEGER,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
