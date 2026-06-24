export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-background">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-center py-32 px-16">
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Ripper
        </h1>
        <p className="mt-2 text-lg text-muted">
          PDF Chapter Splitter
        </p>
      </main>
    </div>
  );
}
