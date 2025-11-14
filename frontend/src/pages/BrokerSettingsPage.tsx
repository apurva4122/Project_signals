import { FormEvent, useEffect, useState } from "react";
import { Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
    MotilalCredentialsInput,
    MotilalCredentialsResponse,
    fetchMotilalCredentials,
    saveMotilalCredentials,
} from "@/lib/api";
import { cn } from "@/lib/utils";

function BrokerSettingsPage(): JSX.Element {
    const [form, setForm] = useState<MotilalCredentialsInput>({
        api_key: "",
        client_code: "",
        auth_token: "",
        totp_secret: "",
    });
    const [status, setStatus] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await fetchMotilalCredentials();
                if (data) {
                    setForm((prev) => ({
                        ...prev,
                        api_key: data.api_key,
                        client_code: data.client_code,
                        auth_token: "",
                        totp_secret: "",
                    }));
                }
            } catch (error) {
                setStatus(error instanceof Error ? error.message : String(error));
            }
        };
        void load();
    }, []);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSaving(true);
        setStatus(null);
        try {
            const payload: MotilalCredentialsInput = {
                api_key: form.api_key.trim(),
                client_code: form.client_code.trim(),
                auth_token: form.auth_token.trim(),
            };
            if (form.totp_secret?.trim()) {
                payload.totp_secret = form.totp_secret.trim();
            }
            const response = await saveMotilalCredentials(payload);
            setStatus(`Credentials saved. Updated at ${new Date(response.updated_at).toLocaleString()}`);
            setForm((prev) => ({ ...prev, auth_token: "", totp_secret: "" }));
        } catch (error) {
            setStatus(error instanceof Error ? error.message : String(error));
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="mx-auto max-w-3xl">
            <Card>
                <CardHeader>
                    <CardTitle>Motilal Oswal Integration</CardTitle>
                    <CardDescription>
                        Provide your Motilal Oswal API credentials. Each user maintains their own connection. Tokens remain on your
                        machine.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form className="grid gap-6" onSubmit={handleSubmit}>
                        <div className="grid gap-2">
                            <Label htmlFor="apiKey">API Key</Label>
                            <Input
                                id="apiKey"
                                value={form.api_key}
                                onChange={(event) => setForm((prev) => ({ ...prev, api_key: event.target.value }))}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="clientCode">Client Code</Label>
                            <Input
                                id="clientCode"
                                value={form.client_code}
                                onChange={(event) => setForm((prev) => ({ ...prev, client_code: event.target.value }))}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="authToken">Auth Token</Label>
                            <Input
                                id="authToken"
                                value={form.auth_token}
                                onChange={(event) => setForm((prev) => ({ ...prev, auth_token: event.target.value }))}
                                placeholder="Paste the auth token returned after Motilal login"
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="totpSecret">TOTP Secret (optional)</Label>
                            <Input
                                id="totpSecret"
                                value={form.totp_secret}
                                onChange={(event) => setForm((prev) => ({ ...prev, totp_secret: event.target.value }))}
                                placeholder="Enable automatic refresh by supplying the TOTP secret"
                            />
                        </div>
                        <Separator />
                        <div className="flex items-center gap-3">
                            <Button type="submit" disabled={saving}>
                                <Save className={cn("mr-2 h-4 w-4", saving && "animate-spin")} />
                                Save Credentials
                            </Button>
                            {status && <p className="text-sm text-muted-foreground">{status}</p>}
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

export default BrokerSettingsPage;


