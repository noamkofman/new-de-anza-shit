import { useState, useEffect } from 'react'
import Message from './message'

function App() {
  const [backendValue, setBackendValue] = useState('')
  const [text, setText] = useState('')
  const [choice, setChoice] = useState('Option 1')
  const fetchBackendValue = () => {
    fetch('http://127.0.0.1:8080/members', { cache: 'no-store' })
      .then((res) => res.json())
      .then((data) => {
        setBackendValue(data.members ?? '')
      })
  }

  useEffect(() => {
    fetchBackendValue()
  }, [])
  return (
    <div className="page">
      <Message />
      <p>Backend value: {backendValue}</p>
      <button type="button" onClick={fetchBackendValue}>
        Refresh backend value
      </button>
      <div className="dropdown-card">
        <label htmlFor="user-input">Enter University for Transfer: </label>
        <input
          id="user-input"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Enter Text"
        />
        
        <label htmlFor='simple-dropdown'>Pick one:</label>
        <select
          id="simple-dropdown"
          value={choice}
          onChange={(event) => setChoice(event.target.value)}
        >
          <option>Option 1</option>
          <option>Option 2</option>
          <option>Option 3</option> 
         </select>
        <p>You typed: {text}</p>
      </div>
    </div>
  )
}

export default App
