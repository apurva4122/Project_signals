import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Loader2, Play, RefreshCcw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Instrument, BacktestResponsePayload, BacktestRequestPayload } from "@/lib/api";
import { listInstruments, refreshNifty100, runBacktest } from "@/lib/api";
import { cn } from "@/lib/utils";

const DEFAULT_INITIAL_CAPITAL = 1_000_000;

const now = new Date();
const defaultEnd = new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
const defaultStart = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000 - now.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 16);

function BacktestPage(): JSX.Element {
    const [instruments, setInstruments] = useState<Instrument[]>([]);
    const [loadingInstruments, setLoadingInstruments] = useState(false);
    const [instrumentStatus, setInstrumentStatus] = useState<string | null>(null);

    const [form, setForm] = useState({
        strategy_id: "nifty-test",
        symbol: "",
        start: defaultStart,
        end: defaultEnd,
        initial_capital: DEFAULT_INITIAL_CAPITAL,
    });
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState<BacktestResponsePayload | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            setLoadingInstruments(true);
            try {
                const data = await listInstruments();
                setInstruments(data);
                if (!form.symbol && data.length) {
                    setForm((prev) => ({ ...prev, symbol: data[0]!.symbol }));
                }
            } catch (err) {
                setInstrumentStatus(err instanceof Error ? err.message : String(err));
            } finally {
                setLoadingInstruments(false);
            }
        };
        void load();
    }, []);

    const handleRefreshInstruments = async () => {
        setLoadingInstruments(true);
        setInstrumentStatus(null);
        try {
            const data = await refreshNifty100();
            setInstruments(data);
            setInstrumentStatus(`Loaded ${data.length} instruments from Motilal Oswal.`);
            if (!data.find((item: Instrument) => item.symbol === form.symbol) && data.length) {
                setForm((prev) => ({ ...prev, symbol: data[0]!.symbol }));
            }
        } catch (err) {
            setInstrumentStatus(err instanceof Error ? err.message : String(err));
        } finally {
            setLoadingInstruments(false);
        }
    };

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSubmitting(true);
        setError(null);
        setResult(null);
        try {
            if (!form.symbol) {
                throw new Error("Select a symbol before running backtest.");
            }
            const payload: BacktestRequestPayload = {
                strategy_id: form.strategy_id.trim(),
                symbols: [form.symbol],
                start: new Date(form.start).toISOString(),
                end: new Date(form.end).toISOString(),
                initial_capital: Number(form.initial_capital),
            };
            const response = await runBacktest(payload);
            setResult(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : String(err));
        } finally {
            setSubmitting(false);
        }
    };

    const symbolOptions = useMemo(() => instruments.map((instrument) => instrument.symbol), [instruments]);

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                        <CardTitle>NIFTY 100 Universe</CardTitle>
                        <CardDescription>Pull the latest instrument list directly via your Motilal Oswal connection.</CardDescription>
                    </div>
                    <Button variant="outline" onClick={() => void handleRefreshInstruments()} disabled={loadingInstruments}>
                        <RefreshCcw className={cn("mr-2 h-4 w-4", loadingInstruments && "animate-spin")} />
                        Refresh from Broker
                    </Button>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-wrap gap-2">
                        {loadingInstruments ? (
                            <span className="text-sm text-muted-foreground">Fetching instruments…</span>
                        ) : (
                            symbolOptions.slice(0, 20).map((symbol) => (
                                <Badge key={symbol} variant="outline">
                                    {symbol}
                                </Badge>
                            ))
                        )}
                    </div>
                    {instrumentStatus && <p className="mt-3 text-sm text-muted-foreground">{instrumentStatus}</p>}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>60-Day Intraday Backtest</CardTitle>
                    <CardDescription>
                        Backtests use 5-minute bars fetched on demand from Motilal Oswal whenever you submit a run.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
                        <div className="grid gap-2">
                            <Label htmlFor="strategy">Strategy ID</Label>
                            <Input
                                id="strategy"
                                value={form.strategy_id}
                                onChange={(event) => setForm((prev) => ({ ...prev, strategy_id: event.target.value }))}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label>Select Symbol</Label>
                            <Select value={form.symbol} onValueChange={(value) => setForm((prev) => ({ ...prev, symbol: value }))}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Choose instrument" />
                                </SelectTrigger>
                                <SelectContent>
                                    {symbolOptions.map((symbol) => (
                                        <SelectItem key={symbol} value={symbol}>
                                            {symbol}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="start">Start Date</Label>
                            <Input
                                id="start"
                                type="datetime-local"
                                value={form.start}
                                onChange={(event) => setForm((prev) => ({ ...prev, start: event.target.value }))}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="end">End Date</Label>
                            <Input
                                id="end"
                                type="datetime-local"
                                value={form.end}
                                onChange={(event) => setForm((prev) => ({ ...prev, end: event.target.value }))}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="capital">Initial Capital (₹)</Label>
                            <Input
                                id="capital"
                                type="number"
                                min={1}
                                value={form.initial_capital}
                                onChange={(event) =>
                                    setForm((prev) => ({ ...prev, initial_capital: Number(event.target.value) || DEFAULT_INITIAL_CAPITAL }))
                                }
                            />
                        </div>
                        <div className="md:col-span-2 flex flex-wrap items-center gap-4">
                            <Button type="submit" disabled={submitting || !form.symbol}>
                                {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                                Run Backtest
                            </Button>
                            {error && <span className="text-sm text-destructive">{error}</span>}
                            {result && (
                                <Badge variant="secondary">
                                    {result.backtest_id} • Return {(result.metrics.total_return * 100).toFixed(2)}% • Final Equity ₹
                                    {result.metrics.final_equity.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                                </Badge>
                            )}
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

export default BacktestPage;


