import type { PriorityType, StatusType, Task } from "../components/TaskList";
import { ApiError } from "./error";

type TaskCreate = {
    title: string
    priority: PriorityType
    status?: StatusType
    project_id?: number|null
    category_id?: number|null
    tag_ids?: number[]|null
}

type TaskUpdate = {
    status?: StatusType
}

export async function createTask(token: string | null, task: TaskCreate): Promise<Task> {

    const response = await fetch("http://localhost:8000/tasks", {
        method: "POST",
        body: JSON.stringify(task),
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    })

    if (!response.ok) {
        const err_body = await response.json()
        throw new ApiError(`createTask error: ${response.status} - ${response.statusText}`, response.status, err_body)
    }

    return await response.json()
}

export async function deleteTask(token: string | null, task_id: number) {

    const response = await fetch(`http://localhost:8000/tasks/${task_id}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
        }
    })

    if (!response.ok) {
        const err_body = await response.json()
        throw new ApiError(`deleteTask error: ${response.status} - ${response.statusText}`, response.status, err_body)
    }

    return response.status
}

export async function updateTask(token: string | null, task_id: number, changes: TaskUpdate): Promise<Task> {

    const response = await fetch(`http://localhost:8000/tasks/${task_id}`, {
        method: "PATCH",
        body: JSON.stringify(changes),
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        }
    })

    if (!response.ok) {
        const err_body = await response.json()
        throw new ApiError(`updateTask error : ${response.status} - ${response.statusText}`, response.status, err_body)
    }

    return response.json()
}