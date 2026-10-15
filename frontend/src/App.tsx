import { useState, useEffect } from 'react'
import './App.css'
import { TaskList, type Task } from './components/TaskList.tsx'

const TASKS_URL = "http://localhost:8000/tasks";

function App() {
  const [newTitle, setNewTitle] = useState('')

  const [tasks, setTasks] = useState<Task[]>([
    { id: 1, title: 'Test 1', done: false },
    { id: 2, title: 'Test 2', done: true },
    { id: 3, title: 'Test 3', done: false },
  ])

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);

  useEffect(() => {
    async function loadTasks() {

      try {
        const token = localStorage.getItem('token');
        const response = await fetch(TASKS_URL, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

      if (!response.ok) {
        const body = await response.json();
        throw new Error(`${response.status} - ${response.statusText}`, {cause: body } )
      }

      setTasks(await response.json());
      } catch (err) {
          if (err instanceof Error) {
            setError(err.message)
          } else {
            setError("Error desconocido.")
          }
      } finally {
        setIsLoading(false);
      }
    }
      loadTasks()
  }, [])

  function toggleTask(id: number) {
    const updatedTasks = tasks.map((task) =>
      task.id === id ? { ...task, done: !task.done } : task,
    )

    setTasks(updatedTasks)
  }

  function addTask() {
    if (newTitle.trim().length === 0) {
      setNewTitle('')
      return
    }

    const newTask = {
      id: Date.now(),
      title: newTitle.trim(),
      done: false,
    }

    setTasks([...tasks, newTask])

    setNewTitle('')
  }

  return (
    <>
      <input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
      <button onClick={() => addTask()}>Agregar Tarea</button>

      {isLoading ? (
        <p>Cargando...</p>
      ): error !== null ? (
        <p>Ocurrio un error al recuperar tareas : {error}</p>
      ): (
      <TaskList tasks={tasks} onToggle={toggleTask} />
      )}
    </>
  )
}

export default App
