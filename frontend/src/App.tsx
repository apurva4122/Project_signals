import { useEffect, useMemo, useState } from "react";
import { RefreshCcw, Send, Play, PlugZap } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import { apiFetch, API_BASE_URL, cn } from "@/lib/utils";

type Position = {
  symbol: string;
  quantity: number;
  avg_price: number;
};

type AccountSnapshot = {
  cash_balance: number;
  margin_used: number;
  positions: Position[];
};

type Instrument = {
  symbol: string;
  exchange: string;
  segment: string;
};

type OrderResponse = {
  order_id: string;
  status: string;
  filled_quantity: number;
  avg_fill_price: number | null;
  timestamp: string;
};

type BacktestResponse = {
  backtest_id: string;
  metrics: {
    total_return: number;
    final_equity: number;
  };
};

const DEFAULT_SYMBOLS = ["RELIANCE", "INFY", "NIFTY50"];

const now = new Date();
const defaultEnd = new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
const defaultStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000 - now.getTimezoneOffset() * 60_000)
  .toISOString()
  .slice(0, 16);

function App() {
  const [account, setAccount] = useState<AccountSnapshot | null>(null);
  const [accountLoading, setAccountLoading] = useState(false);
  const [accountError, setAccountError] = useState<string | null>(null);

  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [instrumentForm, setInstrumentForm] = useState({
    symbol: "",
    exchange: "NSE",
    segment: "EQ",
    lot_size: "",
    tick_size: "0.05",
  });
  const [instrumentMessage, setInstrumentMessage] = useState<string | null>(null);
  const [instrumentError, setInstrumentError] = useState<string | null>(null);
  const [instrumentSubmitting, setInstrumentSubmitting] = useState(false);

  const [orderForm, setOrderForm] = useState({
    symbol: "",
    side: "BUY",
    order_type: "MARKET",
    quantity: 1,
    price: "",
    strategy_id: "demo",
  });
  const [orderResult, setOrderResult] = useState<OrderResponse | null>(null);
  const [orderError, setOrderError] = useState<string | null>(null);
  const [orderSubmitting, setOrderSubmitting] = useState(false);

  const [backtestForm, setBacktestForm] = useState({
    strategy_id: "mean-reversion",
    symbols: "RELIANCE",
    start: defaultStart,
    end: defaultEnd,
    initial_capital: 1_000_000,
  });
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null);
  const [backtestError, setBacktestError] = useState<string | null>(null);
  const [backtestSubmitting, setBacktestSubmitting] = useState(false);

  const [chartinkPayload, setChartinkPayload] = useState('{"symbol":"RELIANCE","action":"BUY"}');
  const [tradingviewPayload, setTradingviewPayload] = useState(
    '{"strategy_id":"mean-reversion","action":"BUY","symbol":"RELIANCE"}',
  );
  const [chartinkToken, setChartinkToken] = useState<string>("");
  const [tradingviewToken, setTradingviewToken] = useState<string>("");
  const [webhookMessage, setWebhookMessage] = useState<string | null>(null);
  const [webhookError, setWebhookError] = useState<string | null>(null);
  const [webhookSubmitting, setWebhookSubmitting] = useState<"chartink" | "tradingview" | null>(null);

  const knownSymbols = useMemo(() => {
    const set = new Set<string>();
    DEFAULT_SYMBOLS.forEach((sym) => set.add(sym));
    instruments.forEach((instrument) => set.add(instrument.symbol));
    if (orderForm.symbol) set.add(orderForm.symbol);
    return Array.from(set);
  }, [instruments, orderForm.symbol]);

  const baseUrlNote = `Target API: ${API_BASE_URL}`;

  const loadAccount = async () => {
    setAccountLoading(true);
    setAccountError(null);
    try {
      const data = await apiFetch<AccountSnapshot>("/api/v1/accounts/primary");
      setAccount(data);
    } catch (error) {
      setAccountError(error instanceof Error ? error.message : String(error));
    } finally {
      setAccountLoading(false);
    }
  };

  const loadInstruments = async () => {
    try {
      const data = await apiFetch<Instrument[]>("/api/v1/instruments/");
      setInstruments(data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    void loadAccount();
    void loadInstruments();
  }, []);

  useEffect(() => {
    if (!orderForm.symbol && instruments.length > 0) {
      setOrderForm((prev) => ({ ...prev, symbol: instruments[0]?.symbol ?? DEFAULT_SYMBOLS[0] }));
    }
  }, [instruments, orderForm.symbol]);

  const handleInstrumentSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setInstrumentSubmitting(true);
    setInstrumentError(null);
    setInstrumentMessage(null);
    try {
      if (!instrumentForm.symbol.trim()) {
        throw new Error("Symbol is required");
      }
      const payload = {
        symbol: instrumentForm.symbol.trim().toUpperCase(),
        exchange: instrumentForm.exchange || "NSE",
        segment: instrumentForm.segment as Instrument["segment"],
        lot_size: instrumentForm.lot_size ? Number(instrumentForm.lot_size) : null,
        tick_size: instrumentForm.tick_size ? Number(instrumentForm.tick_size) : 0.05,
      };
      await apiFetch<Instrument>("/api/v1/instruments/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setInstrumentMessage(`Instrument ${payload.symbol} saved`);
      setInstrumentForm((prev) => ({ ...prev, symbol: "" }));
      void loadInstruments();
    } catch (error) {
      setInstrumentError(error instanceof Error ? error.message : String(error));
    } finally {
      setInstrumentSubmitting(false);
    }
  };

  const handleOrderSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setOrderSubmitting(true);
    setOrderError(null);
    setOrderResult(null);
    try {
      if (!orderForm.symbol) {
        throw new Error("Select a symbol");
      }
      const payload = {
        symbol: orderForm.symbol,
        side: orderForm.side,
        order_type: orderForm.order_type,
        quantity: Number(orderForm.quantity),
        strategy_id: orderForm.strategy_id,
        price: orderForm.price ? Number(orderForm.price) : undefined,
      };
      if (!Number.isFinite(payload.quantity) || payload.quantity <= 0) {
        throw new Error("Quantity must be greater than zero");
      }
      const response = await apiFetch<OrderResponse>("/api/v1/orders/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setOrderResult(response);
      void loadAccount();
    } catch (error) {
      setOrderError(error instanceof Error ? error.message : String(error));
    } finally {
      setOrderSubmitting(false);
    }
  };

  const handleBacktestSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBacktestSubmitting(true);
    setBacktestError(null);
    setBacktestResult(null);
    try {
      if (!backtestForm.symbols.trim()) {
        throw new Error("Provide at least one symbol");
      }
      const payload = {
        strategy_id: backtestForm.strategy_id,
        symbols: backtestForm.symbols.split(",").map((sym) => sym.trim()).filter(Boolean),
        start: new Date(backtestForm.start).toISOString(),
        end: new Date(backtestForm.end).toISOString(),
        initial_capital: Number(backtestForm.initial_capital),
      };
      const response = await apiFetch<BacktestResponse>("/api/v1/backtests/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setBacktestResult(response);
    } catch (error) {
      setBacktestError(error instanceof Error ? error.message : String(error));
    } finally {
      setBacktestSubmitting(false);
    }
  };

  const handleWebhookSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
    provider: "chartink" | "tradingview",
  ) => {
    event.preventDefault();
    setWebhookSubmitting(provider);
    setWebhookMessage(null);
    setWebhookError(null);
    try {
      const body = provider === "chartink" ? chartinkPayload : tradingviewPayload;
      const headerKey = provider === "chartink" ? "X-Chartink-Token" : "X-TradingView-Token";
      const token = provider === "chartink" ? chartinkToken : tradingviewToken;
      const parsed = JSON.parse(body || "{}");
      const response = await apiFetch<{ status: string; received_at: string }>(
        `/api/v1/webhooks/${provider}`,
        {
          method: "POST",
          body: JSON.stringify(parsed),
          headers: token ? { [headerKey]: token } : {},
        },
      );
      setWebhookMessage(`${provider} accepted (${response.received_at})`);
    } catch (error) {
      setWebhookError(error instanceof Error ? error.message : String(error));
    } finally {
      setWebhookSubmitting(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/40">
        <div className="container flex flex-col gap-2 py-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold">Project Signals Console</h1>
              <p className="text-sm text-muted-foreground">Manage paper trades, backtests, and webhook-driven signals.</p>
            </div>
            <Badge variant="secondary">{baseUrlNote}</Badge>
          </div>
          <Separator className="bg-border" />
        </div>
      </header>

      <main className="container py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="backtests">Backtests</TabsTrigger>
            <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <section className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Account Snapshot</CardTitle>
                    <CardDescription>Latest balances and open positions</CardDescription>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => void loadAccount()} disabled={accountLoading}>
                    <RefreshCcw className={cn("h-4 w-4", accountLoading && "animate-spin")} />
                    <span className="sr-only">Refresh account</span>
                  </Button>
                </CardHeader>
                <CardContent className="space-y-4">
                  {accountError ? (
                    <p className="text-sm text-destructive">{accountError}</p>
                  ) : (
                    <div className="grid gap-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Cash Balance</span>
                        <span className="font-medium">
                          ₹{account?.cash_balance?.toLocaleString("en-IN", { maximumFractionDigits: 2 }) ?? "—"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Margin Used</span>
                        <span className="font-medium">
                          ₹{account?.margin_used?.toLocaleString("en-IN", { maximumFractionDigits: 2 }) ?? "—"}
                        </span>
                      </div>
                    </div>
                  )}
                  <Separator />
                  <div>
                    <h3 className="mb-2 text-sm font-semibold">Open Positions</h3>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Symbol</TableHead>
                          <TableHead>Quantity</TableHead>
                          <TableHead>Avg. Price</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {account?.positions?.length ? (
                          account.positions.map((position) => (
                            <TableRow key={position.symbol}>
                              <TableCell>{position.symbol}</TableCell>
                              <TableCell>{position.quantity}</TableCell>
                              <TableCell>₹{position.avg_price.toFixed(2)}</TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={3} className="text-center text-sm text-muted-foreground">
                              No open positions yet.
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                      <TableCaption>Positions refresh automatically after each simulated fill.</TableCaption>
                    </Table>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Instrument Catalogue</CardTitle>
                  <CardDescription>Add instruments for orders and strategy backtests.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <form className="space-y-4" onSubmit={handleInstrumentSubmit}>
                    <div className="grid gap-2">
                      <Label htmlFor="symbol">Symbol</Label>
                      <Input
                        id="symbol"
                        placeholder="e.g. RELIANCE"
                        value={instrumentForm.symbol}
                        onChange={(event) => setInstrumentForm((prev) => ({ ...prev, symbol: event.target.value }))}
                        required
                      />
                    </div>
                    <div className="grid gap-2 md:grid-cols-2">
                      <div className="grid gap-2">
                        <Label htmlFor="exchange">Exchange</Label>
                        <Input
                          id="exchange"
                          value={instrumentForm.exchange}
                          onChange={(event) => setInstrumentForm((prev) => ({ ...prev, exchange: event.target.value }))}
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="segment">Segment</Label>
                        <Input
                          id="segment"
                          value={instrumentForm.segment}
                          onChange={(event) => setInstrumentForm((prev) => ({ ...prev, segment: event.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="grid gap-2 md:grid-cols-2">
                      <div className="grid gap-2">
                        <Label htmlFor="lotSize">Lot Size</Label>
                        <Input
                          id="lotSize"
                          type="number"
                          min={0}
                          placeholder="Optional"
                          value={instrumentForm.lot_size}
                          onChange={(event) => setInstrumentForm((prev) => ({ ...prev, lot_size: event.target.value }))}
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="tickSize">Tick Size</Label>
                        <Input
                          id="tickSize"
                          type="number"
                          step="0.01"
                          value={instrumentForm.tick_size}
                          onChange={(event) => setInstrumentForm((prev) => ({ ...prev, tick_size: event.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Button type="submit" disabled={instrumentSubmitting}>
                        <Send className={cn("mr-2 h-4 w-4", instrumentSubmitting && "animate-spin")} />
                        Save Instrument
                      </Button>
                      {instrumentMessage && <span className="text-sm text-muted-foreground">{instrumentMessage}</span>}
                      {instrumentError && <span className="text-sm text-destructive">{instrumentError}</span>}
                    </div>
                  </form>
                  <Separator />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium text-foreground">Tracked Symbols</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {knownSymbols.map((symbol) => (
                        <Badge key={symbol} variant="outline">
                          {symbol}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>
          </TabsContent>

          <TabsContent value="orders">
            <Card>
              <CardHeader>
                <CardTitle>Submit Paper Order</CardTitle>
                <CardDescription>Orders are simulated via the Project Signals execution engine.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <form className="grid gap-4 md:grid-cols-2" onSubmit={handleOrderSubmit}>
                  <div className="grid gap-2">
                    <Label>Symbol</Label>
                    <Select
                      value={orderForm.symbol}
                      onValueChange={(value) => setOrderForm((prev) => ({ ...prev, symbol: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select symbol" />
                      </SelectTrigger>
                      <SelectContent>
                        {knownSymbols.map((symbol) => (
                          <SelectItem key={symbol} value={symbol}>
                            {symbol}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Strategy ID</Label>
                    <Input
                      value={orderForm.strategy_id}
                      onChange={(event) => setOrderForm((prev) => ({ ...prev, strategy_id: event.target.value }))}
                      placeholder="demo"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Side</Label>
                    <Select value={orderForm.side} onValueChange={(value) => setOrderForm((prev) => ({ ...prev, side: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BUY">Buy</SelectItem>
                        <SelectItem value="SELL">Sell</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Order Type</Label>
                    <Select
                      value={orderForm.order_type}
                      onValueChange={(value) => setOrderForm((prev) => ({ ...prev, order_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MARKET">Market</SelectItem>
                        <SelectItem value="LIMIT">Limit</SelectItem>
                        <SelectItem value="STOP">Stop</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Quantity</Label>
                    <Input
                      type="number"
                      min={1}
                      value={orderForm.quantity}
                      onChange={(event) =>
                        setOrderForm((prev) => ({ ...prev, quantity: Number(event.target.value) }))
                      }
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Price (optional)</Label>
                    <Input
                      type="number"
                      step="0.05"
                      value={orderForm.price}
                      onChange={(event) => setOrderForm((prev) => ({ ...prev, price: event.target.value }))}
                      placeholder="Auto for market order"
                    />
                  </div>
                  <div className="md:col-span-2 flex flex-wrap items-center gap-3">
                    <Button type="submit" disabled={orderSubmitting}>
                      <Send className={cn("mr-2 h-4 w-4", orderSubmitting && "animate-spin")} />
                      Submit Order
                    </Button>
                    {orderResult && (
                      <Badge variant="secondary">
                        {orderResult.status} • Qty {orderResult.filled_quantity}
                        {orderResult.avg_fill_price ? ` @ ₹${orderResult.avg_fill_price.toFixed(2)}` : ""}
                      </Badge>
                    )}
                    {orderError && <span className="text-sm text-destructive">{orderError}</span>}
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="backtests">
            <Card>
              <CardHeader>
                <CardTitle>Run Historical Backtest</CardTitle>
                <CardDescription>Uses the mock CSV market data provider configured on the backend.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <form className="grid gap-4 md:grid-cols-2" onSubmit={handleBacktestSubmit}>
                  <div className="grid gap-2">
                    <Label>Strategy ID</Label>
                    <Input
                      value={backtestForm.strategy_id}
                      onChange={(event) => setBacktestForm((prev) => ({ ...prev, strategy_id: event.target.value }))}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Symbols (comma separated)</Label>
                    <Input
                      value={backtestForm.symbols}
                      onChange={(event) => setBacktestForm((prev) => ({ ...prev, symbols: event.target.value }))}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Start</Label>
                    <Input
                      type="datetime-local"
                      value={backtestForm.start}
                      onChange={(event) => setBacktestForm((prev) => ({ ...prev, start: event.target.value }))}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>End</Label>
                    <Input
                      type="datetime-local"
                      value={backtestForm.end}
                      onChange={(event) => setBacktestForm((prev) => ({ ...prev, end: event.target.value }))}
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Initial Capital (₹)</Label>
                    <Input
                      type="number"
                      min={1}
                      value={backtestForm.initial_capital}
                      onChange={(event) =>
                        setBacktestForm((prev) => ({ ...prev, initial_capital: Number(event.target.value) }))
                      }
                    />
                  </div>
                  <div className="md:col-span-2 flex flex-wrap items-center gap-3">
                    <Button type="submit" disabled={backtestSubmitting}>
                      <Play className={cn("mr-2 h-4 w-4", backtestSubmitting && "animate-spin")} />
                      Run Backtest
                    </Button>
                    {backtestResult && (
                      <Badge variant="secondary">
                        Backtest {backtestResult.backtest_id} • Return {(backtestResult.metrics.total_return * 100).toFixed(2)}%
                      </Badge>
                    )}
                    {backtestError && <span className="text-sm text-destructive">{backtestError}</span>}
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="webhooks">
            <Card>
              <CardHeader>
                <CardTitle>Webhook Tester</CardTitle>
                <CardDescription>Send sample payloads from Chartink and TradingView into the webhook ingress.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-6 md:grid-cols-2">
                <form className="space-y-4" onSubmit={(event) => handleWebhookSubmit(event, "chartink")}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Chartink</p>
                      <p className="text-sm text-muted-foreground">POST /api/v1/webhooks/chartink</p>
                    </div>
                    <PlugZap className="h-5 w-5 text-primary" />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="chartink-token">Token (optional override)</Label>
                    <Input
                      id="chartink-token"
                      value={chartinkToken}
                      onChange={(event) => setChartinkToken(event.target.value)}
                      placeholder="Matches backend .env token"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="chartink-payload">Payload JSON</Label>
                    <Textarea
                      id="chartink-payload"
                      value={chartinkPayload}
                      onChange={(event) => setChartinkPayload(event.target.value)}
                      rows={8}
                    />
                  </div>
                  <Button type="submit" disabled={webhookSubmitting === "chartink"}>
                    <Send className={cn("mr-2 h-4 w-4", webhookSubmitting === "chartink" && "animate-spin")} />
                    Dispatch
                  </Button>
                </form>

                <form className="space-y-4" onSubmit={(event) => handleWebhookSubmit(event, "tradingview")}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">TradingView</p>
                      <p className="text-sm text-muted-foreground">POST /api/v1/webhooks/tradingview</p>
                    </div>
                    <PlugZap className="h-5 w-5 text-primary" />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="tradingview-token">Token (optional override)</Label>
                    <Input
                      id="tradingview-token"
                      value={tradingviewToken}
                      onChange={(event) => setTradingviewToken(event.target.value)}
                      placeholder="Matches backend .env token"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="tradingview-payload">Payload JSON</Label>
                    <Textarea
                      id="tradingview-payload"
                      value={tradingviewPayload}
                      onChange={(event) => setTradingviewPayload(event.target.value)}
                      rows={8}
                    />
                  </div>
                  <Button type="submit" disabled={webhookSubmitting === "tradingview"}>
                    <Send className={cn("mr-2 h-4 w-4", webhookSubmitting === "tradingview" && "animate-spin")} />
                    Dispatch
                  </Button>
                </form>
              </CardContent>
              {(webhookMessage || webhookError) && (
                <div className="px-6 pb-6">
                  {webhookMessage && <p className="text-sm text-muted-foreground">{webhookMessage}</p>}
                  {webhookError && <p className="text-sm text-destructive">{webhookError}</p>}
                </div>
              )}
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default App;
