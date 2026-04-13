import './App.css'
import { Button } from "@/components/ui/button"
import { useConnection } from "@/hooks/core/useConnection"

function App() {
  const { connect } = useConnection()
  
  return (
    <>
      <h1 className="text-3xl font-bold underline">
        Hello world!
      </h1>
      <Button onClick={connect}>Connect</Button>
    </>
  )
}

export default App
