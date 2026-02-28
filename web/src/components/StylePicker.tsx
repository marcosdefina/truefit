import { useStore, type StyleOption } from '../store/useStore'

const STYLES: { value: StyleOption; label: string; icon: string; desc: string }[] = [
  { value: 'casual', label: 'Casual', icon: '👕', desc: 'Relaxed everyday wear' },
  { value: 'smart-casual', label: 'Smart Casual', icon: '👔', desc: 'Polished but approachable' },
  { value: 'formal', label: 'Formal', icon: '🤵', desc: 'Business & evening wear' },
  { value: 'streetwear', label: 'Streetwear', icon: '🧢', desc: 'Urban, bold, trendy' },
  { value: 'minimal', label: 'Minimal', icon: '◻️', desc: 'Clean lines, neutral tones' },
]

export default function StylePicker() {
  const { style, setStyle } = useStore()

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-brand-700">Style</label>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {STYLES.map((s) => (
          <button
            key={s.value}
            onClick={() => setStyle(s.value)}
            className={`p-4 rounded-xl border-2 text-left transition-all duration-150 ${
              style === s.value
                ? 'border-brand-600 bg-brand-50 shadow-md'
                : 'border-brand-100 bg-white hover:border-brand-300'
            }`}
          >
            <div className="text-2xl mb-1">{s.icon}</div>
            <div className="font-semibold text-sm text-brand-800">{s.label}</div>
            <div className="text-xs text-brand-500 mt-0.5">{s.desc}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
