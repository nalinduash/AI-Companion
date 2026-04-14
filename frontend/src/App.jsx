import './App.css'
import { Button } from "@/components/ui/button"
import { useOrchestrator } from "@/hooks/core/useOrchestrator"

function App() {
  const { start, stop } = useOrchestrator()

  return (
    <>
      <h1 className="text-3xl font-bold underline">
        Hello world!
      </h1>
      <Button onClick={start}>Start</Button>
      <Button onClick={stop}>Stop</Button>
    </>
  )
}

export default App
