export default function Loading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6">
      {/* Spinner */}
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 border-4 border-brand-200 rounded-full" />
        <div className="absolute inset-0 border-4 border-transparent border-t-brand-600 rounded-full animate-spin" />
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-xl font-semibold text-brand-800">Generating your outfit…</h2>
        <p className="text-brand-500 text-sm">
          Searching the catalogue, matching colours, scoring combinations.
        </p>
      </div>
    </div>
  )
}
