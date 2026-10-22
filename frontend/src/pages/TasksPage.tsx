import { useState, useEffect } from 'react'
import '../App.css'
import { type PriorityType, TaskList, type Task, PriorityValues } from '../components/TaskList.tsx'
import { useAuth } from '../auth/AuthContext.tsx';
import { createTask, deleteTask, updateTask } from '../api/tasks.ts';
import { ApiError } from '../api/error.ts';
import { API_URL } from '../api/config.ts';

const TASKS_URL = `${API_URL}/tasks`;

function TasksPage() {
  const [newTitle, setNewTitle] = useState('')
  const [priority, setPriority] = useState<PriorityType>("medium")

  const [tasks, setTasks] = useState<Task[]>([])

  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string|null>(null);
  const [taskError, setTaskError] = useState<string|null>(null);

  const { token, logout } = useAuth()

  useEffect(() => {
    async function loadTasks() {

      try {
        const response = await fetch(TASKS_URL, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

      if (!response.ok) {

        if (response.status === 401) 
          return logout()
        else {
          const body = await response.json();
          throw new Error(`${response.status} - ${response.statusText}`, {cause: body } )
        }
      }

      setTasks(await response.json());
      } catch (err) {
          if (err instanceof Error) {
            setLoadError(err.message)
          } else {
            setLoadError("No se puede cargar las tareas. Intenta más tarde")
          }
      } finally {
        setIsLoading(false);
      }
    }
    
    loadTasks()
  }, [token, logout])

  async function toggleTask(task: Task) {

    const newStatus = task.status === 'done' ? 'pending' : 'done'

    try{
      task = await updateTask(token, task.id, {status: newStatus}) 
      const newTasks = tasks.map((t) => t.id === task.id ? task : t)
      setTaskError(null)
      setTasks(newTasks)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout()
      } else if (err instanceof Error) {
        setTaskError(err.message)
      } else {
        setTaskError(`No se puede marcar una tarea`)
      }
    }
  }

  async function addTask() {
    if (newTitle.trim().length === 0) {
      setNewTitle('')
      return
    }

    try {
      const new_task = await createTask(token, {
        title: newTitle.trim(),
        priority: priority,
      })

      setTasks([...tasks, new_task])
      setTaskError(null)
      setNewTitle('')
    } catch (err) {
        if (err instanceof ApiError && err.status === 401)
          logout()
        else if (err instanceof Error) 
          setTaskError(err.message)
        else
          setTaskError("No se puede agregar una tarea nueva")
    }
  }

  async function removeTask(task_id: number) {
    try {
      await deleteTask(token, task_id)
      setTasks(tasks.filter((task) => task.id !== task_id))
      setTaskError(null)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401)
        logout()
      else if (err instanceof Error)
        setTaskError(err.message)
      else
        setTaskError("Error al eliminar tarea")
    }
  }

  return (
    <>
      <div className='tasks-container'>
        <div className='task-input-container'>
          <input className='task-title-input' value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
          <select value={priority} onChange={(e) => setPriority(e.target.value as PriorityType)}>
            {PriorityValues.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <button onClick={() => addTask()}>Agregar Tarea</button>
        </div>

        <div>
          {isLoading ? (
            <p>Cargando...</p>
          ): loadError !== null ? (
            <p className='error'>Ocurrio un error al recuperar tareas : {loadError}</p>
          ): (
          <TaskList tasks={tasks} onToggle={toggleTask} onDelete={removeTask} />
          )}
        </div>

        {taskError !== null ? (
          <p className='error'>Ocurrio un error con una tarea: {taskError}</p>
        ): <></>}
        <button onClick={() => logout()}>Cerrar Sesion</button>
      </div>
    </>
  )
}

export default TasksPage
