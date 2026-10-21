const StatusValues = [
  "pending",
  "in_progress",
  "done"
] as const;

export const PriorityValues = [
  "urgent",
  "high",
  "medium",
  "low"
] as const;

export type StatusType = typeof StatusValues[number];
export type PriorityType = typeof PriorityValues[number];

export type Task = {
  id: number
  title: string
  priority: PriorityType
  status: StatusType
  project_id: number | null
  category_id: number | null
  tags: Array<Tag>
}

export type Tag = {
  id: number
  name: string
}


type TaskItemProps = {
  task: Task
  onToggle: (task: Task) => void
  onDelete: (id: number) => void
}

function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="task-item">
      <span className="task-title">
        {task.status === "done" ? <s>{task.title}</s> : <p>{task.title}</p>}
      </span>
      <button onClick={() => onToggle(task)}>
        {task.status === "done" ? 'Deshacer' : 'Marcar'}
      </button>
      <button onClick={() => onDelete(task.id)}>Eliminar Tarea</button>
    </li>
  )
}

export function TaskList({
  tasks,
  onToggle,
  onDelete,
}: {
  tasks: Task[]
  onToggle: (task: Task) => void
  onDelete: (id: number) => void
}) {

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} onToggle={onToggle} onDelete={onDelete} />
      ))}
    </ul>
  )
}
