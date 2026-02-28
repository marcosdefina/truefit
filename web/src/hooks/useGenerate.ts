import { useStore, type GenerateResponse } from '../store/useStore'

const API_BASE = '/api'

export function useGenerate() {
  const { budget, style, size, setOutfits, setStep, setError } = useStore()

  const generate = async () => {
    setStep('loading')
    setError(null)

    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          budget,
          style,
          size,
          shop: 'zara',
        }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`API error ${res.status}: ${text}`)
      }

      const data: GenerateResponse = await res.json()

      if (data.outfits.length === 0) {
        setError('No outfits found matching your criteria. Try increasing the budget or changing the style.')
        setStep('configure')
        return
      }

      setOutfits(data.outfits)
      setStep('results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setStep('configure')
    }
  }

  return { generate }
}
