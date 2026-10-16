import { useState } from "react"

async function login(username: string, password: string) {
    const params = {
      "username": username,
      "password": password
    }
    const searchParams = new URLSearchParams(params)

    const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        body: searchParams
    })

    if (!response.ok) {
        const error_json = await response.json()
        throw new Error(`Login error: ${response.status} - ${response.statusText}`, {cause: error_json })
    }

    const data = await response.json()
    return data.access_token
}

export function LoginForm() {

    // useState / hooks aqui
    const [username, setUsername] = useState<string>("")
    const [password, setPassword] = useState<string>("")
    const [error, setError] = useState<string|null>(null)

    return (
      <>
        <form onSubmit={async (e) => {
            e.preventDefault()
            try {
              const token = await login(username, password)
              localStorage.setItem('token', token);
              setError(null)
            } catch (err) {
              if (err instanceof Error)
                setError(err.message)
              else
                setError("Ocurrio un error. Intenta más tarde")
            }
          }}>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />

          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>

          <button type="submit">Submit</button>
        </form>

        {error !== null ? <p>Ocurrio un error : {error}</p> : <></>}
      </>
    )
}
