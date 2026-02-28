import OutfitCard from '../components/OutfitCard'
import { useStore } from '../store/useStore'

export default function Results() {
  const { outfits, activeOutfitIndex, setActiveOutfitIndex, reset } = useStore()

  if (outfits.length === 0) return null

  const outfit = outfits[activeOutfitIndex]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-900">
            Your <span className="text-brand-600">Outfit</span>
          </h1>
          <p className="text-brand-500 mt-1">
            from <span className="font-semibold">{outfit.shop}</span>
          </p>
        </div>
        <button onClick={reset} className="btn-secondary text-sm">
          ← Start Over
        </button>
      </div>

      {/* Outfit switcher (if multiple) */}
      {outfits.length > 1 && (
        <div className="flex gap-2 items-center">
          <span className="text-sm text-brand-500 mr-2">Options:</span>
          {outfits.map((_, i) => (
            <button
              key={i}
              onClick={() => setActiveOutfitIndex(i)}
              className={`w-9 h-9 rounded-full font-semibold text-sm transition-all ${
                i === activeOutfitIndex
                  ? 'bg-brand-700 text-white shadow-md'
                  : 'bg-brand-100 text-brand-600 hover:bg-brand-200'
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}

      {/* Item cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {outfit.items.map((item, i) => (
          <OutfitCard key={`${item.name}-${i}`} item={item} />
        ))}
      </div>

      {/* Summary bar */}
      <div className="card p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <div>
            <div className="text-xs text-brand-500 uppercase tracking-wide">Total</div>
            <div className="text-2xl font-bold text-brand-800">€{Number(outfit.total).toFixed(2)}</div>
          </div>
          <div>
            <div className="text-xs text-brand-500 uppercase tracking-wide">Match Score</div>
            <div className="text-2xl font-bold text-brand-600">
              {Math.round(outfit.score * 100)}%
            </div>
          </div>
        </div>

        {/* Score breakdown */}
        <div className="flex gap-4 text-xs text-brand-500">
          {Object.entries(outfit.score_breakdown).map(([key, val]) => (
            <div key={key} className="text-center">
              <div className="font-semibold text-brand-700">{Math.round(val * 100)}%</div>
              <div className="capitalize">{key.replace('_', ' ')}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
