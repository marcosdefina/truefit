import { create } from 'zustand'

export type StyleOption = 'casual' | 'smart-casual' | 'formal' | 'streetwear' | 'minimal'

export interface SizeInput {
  top: string
  bottom: string
  shoes: string
}

export interface OutfitItem {
  category: string
  name: string
  price: number
  colour: string | null
  colour_name: string | null
  size: string
  image: string
  url: string
}

export interface Outfit {
  shop: string
  total: number
  score: number
  items: OutfitItem[]
  score_breakdown: Record<string, number>
}

export interface GenerateResponse {
  outfits: Outfit[]
  filters_applied: Record<string, unknown>
}

type Step = 'configure' | 'loading' | 'results'

interface AppState {
  // Step
  step: Step
  setStep: (s: Step) => void

  // Inputs
  budget: number
  setBudget: (b: number) => void
  style: StyleOption
  setStyle: (s: StyleOption) => void
  size: SizeInput
  setSize: (field: keyof SizeInput, value: string) => void

  // Results
  outfits: Outfit[]
  setOutfits: (o: Outfit[]) => void
  activeOutfitIndex: number
  setActiveOutfitIndex: (i: number) => void

  // Error
  error: string | null
  setError: (e: string | null) => void

  // Reset
  reset: () => void
}

const initialState = {
  step: 'configure' as Step,
  budget: 120,
  style: 'smart-casual' as StyleOption,
  size: { top: 'M', bottom: '32', shoes: '43' },
  outfits: [],
  activeOutfitIndex: 0,
  error: null,
}

export const useStore = create<AppState>((set) => ({
  ...initialState,

  setStep: (step) => set({ step }),
  setBudget: (budget) => set({ budget }),
  setStyle: (style) => set({ style }),
  setSize: (field, value) =>
    set((state) => ({
      size: { ...state.size, [field]: value },
    })),
  setOutfits: (outfits) => set({ outfits }),
  setActiveOutfitIndex: (activeOutfitIndex) => set({ activeOutfitIndex }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}))
