import './App.css'
import { useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useOrchestrator } from "@/hooks/core/useOrchestrator"
import { useCoreStore } from "@/stores/useCoreStore"
import Scene from "./components/3d/Scene"

function App() {
  const { start, stop } = useOrchestrator()
  const { isConnected, characters, setCharacters, activeCharacter, setActiveCharacter } = useCoreStore()

  useEffect(() => {
    fetch("http://localhost:8000/api/characters")
      .then((res) => res.json())
      .then((data) => {
        if (data.characters) setCharacters(data.characters)
        if (data.active_character) setActiveCharacter(data.active_character)
      }).catch((err) => console.error(err))
  }, [setCharacters, setActiveCharacter])

  const selectCharacter = async (character) => {
    try {
      const res = await fetch("http://localhost:8000/api/characters/active", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: character,
      })
      if (res.ok) {
        const data = await res.json()
        setActiveCharacter(data.active_character)
      }
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="relative min-h-screen text-white">
      <Scene />
      <header className="absolute flex items-center gap-3 px-4 py-2 rounded-full">
        <h1 className="text-md font-bold">AI COMPANION</h1>
        <Badge className={"text-white"}>
          {isConnected ? "Connected" : "Disconnected"}
        </Badge>
      </header>

      <Card className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[90%] bg-black rounded-2xl p-5 flex flex-col gap-4">
        <CardContent className="p-0 flex flex-col gap-4">
          <div className="flex gap-3 justify-center">
            <Button onClick={start} disabled={isConnected} className="flex-1 font-medium border-0 cursor-pointer rounded-xl transition-all bg-gray-600">Start Conversation</Button>
            <Button onClick={stop} disabled={!isConnected} variant="destructive" className="flex-1  font-medium border-0 cursor-pointer rounded-xl transition-all bg-red-700 text-white">Stop</Button>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-xs text-slate-400 font-semibold px-1">SWITCH CHARACTER</span>
            <div className="flex gap-2.5">
              {Object.entries(characters).map(([key, char]) => {
                const isActive = activeCharacter === key
                return (
                  <Button
                    key={key}
                    onClick={() => selectCharacter(key)}
                    className={`flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all cursor-pointer ${
                      isActive ? "bg-green-800" : "bg-gray-500"
                    }`}
                  >
                  {char.name}
                  </Button>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
