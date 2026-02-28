import { useStore } from './store/useStore'
import Configure from './pages/Configure'
import Loading from './pages/Loading'
import Results from './pages/Results'

export default function App() {
  const { step } = useStore()

  return (
    <div className="min-h-screen">
      {step === 'configure' && <Configure />}
      {step === 'loading' && <Loading />}
      {step === 'results' && <Results />}
    </div>
  )
}
