import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import BacktestPage from "@/pages/BacktestPage";
import BrokerSettingsPage from "@/pages/BrokerSettingsPage";
import PlaceholderPage from "@/pages/PlaceholderPage";

function App(): JSX.Element {
    return (
        <Routes>
            <Route element={<AppShell />}>
                <Route path="/" element={<Navigate to="/backtest" replace />} />
                <Route path="/backtest" element={<BacktestPage />} />
                <Route path="/algotrade" element={<PlaceholderPage title="Algo Trade" />} />
                <Route path="/signals" element={<PlaceholderPage title="Signals" />} />
                <Route path="/settings/broker" element={<BrokerSettingsPage />} />
            </Route>
        </Routes>
    );
}

export default App;


