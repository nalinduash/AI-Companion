import './App.css'
import Scene from "./components/3d/Scene"
import BottomBar from './components/ui/BottomBar'
import Header from './components/ui/Header'

function App() {
  return (
    <div className="min-h-screen">
      <Scene />
      <Header />
      <BottomBar />
    </div>
  )
}

export default App
