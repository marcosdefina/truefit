import { useStore } from '../store/useStore'

export default function BudgetSlider() {
  const { budget, setBudget } = useStore()

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-brand-700">Budget</label>
        <span className="text-2xl font-bold text-brand-800">€{budget}</span>
      </div>
      <input
        type="range"
        min={30}
        max={500}
        step={5}
        value={budget}
        onChange={(e) => setBudget(Number(e.target.value))}
        className="w-full h-2 bg-brand-200 rounded-lg appearance-none cursor-pointer
                   accent-brand-600"
      />
      <div className="flex justify-between text-xs text-brand-400">
        <span>€30</span>
        <span>€500</span>
      </div>
    </div>
  )
}
