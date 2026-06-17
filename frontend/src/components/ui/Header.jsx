import React from 'react'
import { Badge } from './badge'
import { useCoreStore } from '@/stores/useCoreStore'

const Header = () => {
    const { isConnected, userData } = useCoreStore()

    return (
        <header className="flex p-5 gap-5 items-center justify-between">
            <div className="flex gap-5 items-center">
                <h1 className="text-md font-bold text-white">AI COMPANION</h1>
                <Badge variant='secondary'>
                    {isConnected ? "Connected" : "Disconnected"}
                </Badge>
            </div>
            {userData?.name && (
                <span className="text-sm font-medium text-white mr-5">
                    Hi, {userData.name}
                </span>
            )}
        </header>
    )
}

export default Header