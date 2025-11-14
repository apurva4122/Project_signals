import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const createJsonResponse = (data: unknown, init: ResponseInit = {}) => {
    const status = init.status ?? 200;
    const statusText = init.statusText ?? (status >= 200 && status < 300 ? "OK" : "Error");
    return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        statusText,
        json: async () => data,
        text: async () => JSON.stringify(data),
    } as Response);
};

describe("App routing", () => {
    const originalEnv = import.meta.env.VITE_API_BASE_URL;

    beforeEach(() => {
        vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000");
        vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
            const url = typeof input === "string" ? input : input.toString();
            if (url.endsWith("/api/v1/instruments/")) {
                return createJsonResponse([{ symbol: "RELIANCE", exchange: "NSE", segment: "EQ", lot_size: null, tick_size: 0.05 }]);
            }
            if (url.endsWith("/api/v1/backtests/")) {
                return createJsonResponse(
                    { backtest_id: "BT-1", metrics: { total_return: 0.12, final_equity: 1_120_000 } },
                    { status: 202 },
                );
            }
            if (url.endsWith("/api/v1/instruments/refresh/nifty100")) {
                return createJsonResponse([{ symbol: "INFY", exchange: "NSE", segment: "EQ", lot_size: null, tick_size: 0.05 }]);
            }
            if (url.endsWith("/api/v1/brokers/motilal")) {
                return createJsonResponse(null);
            }
            return createJsonResponse({});
        }));
    });

    afterEach(() => {
        vi.restoreAllMocks();
        if (originalEnv) {
            vi.stubEnv("VITE_API_BASE_URL", originalEnv);
        }
    });

    it("renders backtest navigation and loads instruments", async () => {
        render(
            <MemoryRouter initialEntries={["/backtest"]}>
                <App />
            </MemoryRouter>,
        );

        expect(await screen.findByText(/Project Signals/i)).toBeTruthy();
        expect(screen.getByRole("link", { name: /Backtest/ })).toBeTruthy();
        expect(screen.getByRole("link", { name: /Broker Settings/ })).toBeTruthy();

        await waitFor(() => {
            expect(screen.getAllByText(/RELIANCE/).length).toBeGreaterThan(0);
        });
    });
});
