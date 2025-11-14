type PlaceholderPageProps = {
    title: string;
};

function PlaceholderPage({ title }: PlaceholderPageProps): JSX.Element {
    return (
        <div className="rounded-lg border border-dashed border-border bg-card/40 p-12 text-center">
            <h2 className="text-2xl font-semibold">{title}</h2>
            <p className="mt-3 text-sm text-muted-foreground">
                This section is coming soon. It will mirror the corresponding AlgoTest flow in future increments.
            </p>
        </div>
    );
}

export default PlaceholderPage;


