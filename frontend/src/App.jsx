import './App.css'
import { Button } from "@/components/ui/button"
import { useOrchestrator } from "@/hooks/core/useOrchestrator"
import Scene from "./components/3d/Scene"

function App() {
  const { start, stop } = useOrchestrator()

  return (
    <>
      <Scene/>
      <h1 className="text-3xl font-bold underline">
        Hello world!
      </h1>
      <Button onClick={start}>Start</Button>
      <Button onClick={stop}>Stop</Button>
    </>
  )
}

export default App
