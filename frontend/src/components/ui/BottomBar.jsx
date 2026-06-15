import React from 'react'
import { useEffect } from 'react'
import { useOrchestrator } from "@/hooks/core/useOrchestrator"
import { useCoreStore } from "@/stores/useCoreStore"
import { Card, CardContent, CardTitle } from './card';
import { Button } from './button';

function BottomBar() {
    const { start, stop, handleInterrupt } = useOrchestrator()
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
        handleInterrupt();
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
        <Card className="inline-block p-1 absolute bottom-5 left-5">
            <CardContent className="p-1">
                <div className="flex gap-3 justify-center items-center">
                    <Button onClick={start} disabled={isConnected} className="w-40">Start Conversation</Button>
                    <Button onClick={stop} disabled={!isConnected} variant="destructive" className="w-40">Stop</Button>
                </div>
            </CardContent>

            <CardTitle className="p-1 mt-1 pb-0 text-xs">SWITCH CHARACTER</CardTitle>
            <div className="flex gap-2.5 p-1">
                {Object.entries(characters).map(([key, char]) => {
                    const isActive = activeCharacter === key
                    return (
                        <Button
                            key={key}
                            onClick={() => selectCharacter(key)}
                            className={`cursor-pointer ${
                            isActive ? "bg-amber-500" : "bg-black"
                            }`}
                        >
                        {char.name}
                        </Button>
                    )
                })}
            </div>
        </Card>
    )
}

export default BottomBar