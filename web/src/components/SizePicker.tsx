import { useStore } from '../store/useStore'

const TOP_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL']
const BOTTOM_SIZES = ['28', '29', '30', '31', '32', '33', '34', '36', '38']
const SHOE_SIZES = ['38', '39', '40', '41', '42', '43', '44', '45', '46']

function SizeRow({
  label,
  options,
  value,
  onChange,
}: {
  label: string
  options: string[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-brand-600 uppercase tracking-wide">
        {label}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-100 ${
              value === opt
                ? 'bg-brand-700 text-white shadow-sm'
                : 'bg-brand-100 text-brand-600 hover:bg-brand-200'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function SizePicker() {
  const { size, setSize } = useStore()

  return (
    <div className="space-y-4">
      <label className="text-sm font-medium text-brand-700">Sizes</label>
      <SizeRow
        label="Top"
        options={TOP_SIZES}
        value={size.top}
        onChange={(v) => setSize('top', v)}
      />
      <SizeRow
        label="Bottom (waist)"
        options={BOTTOM_SIZES}
        value={size.bottom}
        onChange={(v) => setSize('bottom', v)}
      />
      <SizeRow
        label="Shoes (EU)"
        options={SHOE_SIZES}
        value={size.shoes}
        onChange={(v) => setSize('shoes', v)}
      />
    </div>
  )
}
