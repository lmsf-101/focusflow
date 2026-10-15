export type Task = {
  id: number
  title: string
  done: boolean
}

type TaskItemProps = {
  task: Task
  onToggle: (id: number) => void
}

function TaskItem({ task, onToggle }: TaskItemProps) {
  return (
    <li>
      {task.done ? <s>{task.title}</s> : task.title}
      <button onClick={() => onToggle(task.id)}>
        {task.done ? 'Deshacer' : 'Marcar'}
      </button>
    </li>
  )
}

export function TaskList({
  tasks,
  onToggle,
}: {
  tasks: Task[]
  onToggle: (id: number) => void
}) {
  return (
    <ul>
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} onToggle={onToggle} />
      ))}
    </ul>
  )
}
