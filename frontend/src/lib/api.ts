import { apiFetch } from "./utils";

export type MotilalCredentialsInput = {
    api_key: string;
    client_code: string;
    auth_token: string;
    totp_secret?: string;
};

export type MotilalCredentialsResponse = {
    api_key: string;
    client_code: string;
    has_auth_token: boolean;
    has_totp_secret: boolean;
    updated_at: string;
};

export type Instrument = {
    symbol: string;
    exchange: string;
    segment: string;
    lot_size: number | null;
    tick_size: number;
};

export type BacktestRequestPayload = {
    strategy_id: string;
    symbols: string[];
    start: string;
    end: string;
    initial_capital: number;
};

export type BacktestResponsePayload = {
    backtest_id: string;
    metrics: {
        total_return: number;
        final_equity: number;
    };
};

export async function fetchMotilalCredentials(): Promise<MotilalCredentialsResponse | null> {
    return apiFetch<MotilalCredentialsResponse | null>("/api/v1/brokers/motilal");
}

export async function saveMotilalCredentials(
    payload: MotilalCredentialsInput,
): Promise<MotilalCredentialsResponse> {
    return apiFetch<MotilalCredentialsResponse>("/api/v1/brokers/motilal", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export async function listInstruments(): Promise<Instrument[]> {
    return apiFetch<Instrument[]>("/api/v1/instruments/");
}

export async function refreshNifty100(): Promise<Instrument[]> {
    return apiFetch<Instrument[]>("/api/v1/instruments/refresh/nifty100", {
        method: "POST",
    });
}

export async function runBacktest(payload: BacktestRequestPayload): Promise<BacktestResponsePayload> {
    return apiFetch<BacktestResponsePayload>("/api/v1/backtests/", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}


