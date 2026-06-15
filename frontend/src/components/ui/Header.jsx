import React from 'react'
import { Badge } from './badge'
import { useCoreStore } from '@/stores/useCoreStore'

const Header = () => {
    const { isConnected} = useCoreStore()

    return (
        <header className="flex p-5 gap-5 items-center">
            <h1 className="text-md font-bold text-white">AI COMPANION</h1>
            <Badge variant='secondary'>
                {isConnected ? "Connected" : "Disconnected"}
            </Badge>
        </header>
    )
}

export default Header