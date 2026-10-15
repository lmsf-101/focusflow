import { useState } from 'react'
import './App.css'
import { TaskList, type Task } from './components/TaskList.tsx'

function App() {
  const [titulo, setTitulo] = useState('')

  const [tareas, setTareas] = useState<Task[]>([
    { id: 1, title: 'Test 1', done: false },
    { id: 2, title: 'Test 2', done: true },
    { id: 3, title: 'Test 3', done: false },
  ])

  function toggleTask(id: number) {
    const copiaTareas = tareas.map((tarea) =>
      tarea.id === id ? { ...tarea, done: !tarea.done } : tarea,
    )

    setTareas(copiaTareas)
  }

  function agregarTask() {
    if (titulo.trim().length === 0) {
      setTitulo('')
      return
    }

    const nuevaTarea = {
      id: Date.now(),
      title: titulo.trim(),
      done: false,
    }

    setTareas([...tareas, nuevaTarea])

    setTitulo('')
  }

  return (
    <>
      <input value={titulo} onChange={(e) => setTitulo(e.target.value)} />

      <button onClick={() => agregarTask()}>Agregar Tarea</button>
      <TaskList tasks={tareas} onToggle={toggleTask} />
    </>
  )
}

export default App
