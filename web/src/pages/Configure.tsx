import BudgetSlider from '../components/BudgetSlider'
import StylePicker from '../components/StylePicker'
import SizePicker from '../components/SizePicker'
import { useGenerate } from '../hooks/useGenerate'
import { useStore } from '../store/useStore'

export default function Configure() {
  const { generate } = useGenerate()
  const { error } = useStore()

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-10">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-brand-900 tracking-tight">
          True<span className="text-brand-600">Fit</span>
        </h1>
        <p className="text-brand-500 text-lg">
          Set your budget, pick a style, choose your sizes — we'll build the perfect outfit.
        </p>
      </div>

      {/* Form sections */}
      <div className="card p-6 space-y-8">
        <BudgetSlider />
        <hr className="border-brand-100" />
        <StylePicker />
        <hr className="border-brand-100" />
        <SizePicker />
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Generate button */}
      <div className="text-center">
        <button onClick={generate} className="btn-primary text-lg px-10 py-4">
          Generate Outfit
        </button>
      </div>
    </div>
  )
}
