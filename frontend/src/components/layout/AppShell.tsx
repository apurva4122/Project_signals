import { NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";

const navItems = [
    { to: "/backtest", label: "Backtest" },
    { to: "/algotrade", label: "Algo Trade" },
    { to: "/signals", label: "Signals" },
    { to: "/settings/broker", label: "Broker Settings" },
];

export function AppShell(): JSX.Element {
    return (
        <div className="min-h-screen bg-background text-foreground">
            <header className="border-b border-border bg-card/60">
                <div className="container flex items-center justify-between py-4">
                    <div>
                        <h1 className="text-xl font-semibold">Project Signals</h1>
                        <p className="text-sm text-muted-foreground">Paper trading &amp; backtesting for Indian markets</p>
                    </div>
                    <nav className="flex items-center gap-3">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end
                                className={({ isActive }) =>
                                    cn(
                                        "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                        isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground",
                                    )
                                }
                            >
                                {item.label}
                            </NavLink>
                        ))}
                    </nav>
                </div>
            </header>
            <main className="container py-8">
                <Outlet />
            </main>
        </div>
    );
}


