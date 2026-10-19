
const StatusValues = [
  "pending",
  "in_progress",
  "done"
] as const;

const PriorityValues = [
  "urgent",
  "high",
  "medium",
  "low"
] as const;

type StatusType = typeof StatusValues[number];
type PriorityType = typeof PriorityValues[number];

export type Task = {
  id: number
  title: string
  priority: PriorityType
  status: StatusType
  project_id: number | null
  category_id: number | null
  tags: Array<Tag>
}

type Tag = {
  id: number
  name: string
}


type TaskItemProps = {
  task: Task
  onToggle: (id: number) => void
}

function TaskItem({ task, onToggle }: TaskItemProps) {
  return (
    <li>
      {task.status === "done" ? <s>{task.title}</s> : task.title}
      <button onClick={() => onToggle(task.id)}>
        {task.status === "done" ? 'Deshacer' : 'Marcar'}
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
