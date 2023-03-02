import { useEffect, useState } from 'react'

declare global {
  interface Window {
    plotly_figure: any
  }
}

function App() {
  const [data, setData] = useState('')

  useEffect(() => {
    const interval = setInterval(() => {
      setData(JSON.stringify(window))
    }, 100)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="App">
      <h1>Hello from react wowoowow</h1>
      <p className="read-the-docs">
        {data}
      </p>
    </div>
  )
}

export default App
