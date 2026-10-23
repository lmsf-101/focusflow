import { useEffect, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router"
import { useAuth } from "../auth/AuthContext"
import { API_URL } from "../api/config"

async function requestToken(username: string, password: string) {
    const params = {
      "username": username,
      "password": password
    }
    const searchParams = new URLSearchParams(params)

    const response = await fetch(`${API_URL}/token`, {
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

    const { login } = useAuth()
    const [username, setUsername] = useState<string>("")
    const [password, setPassword] = useState<string>("")
    const [error, setError] = useState<string|null>(null)

    const navigate = useNavigate()
    const location = useLocation()

    const [notice, setNotice ] = useState<string|null>(location.state)

    useEffect(() => {
        if (location.state) {
          navigate(location.pathname, {replace: true})
        }
    }, [location, navigate])

    return (
      <>
        <form className="auth-form" onSubmit={async (e) => {
            e.preventDefault()
            try {
              setNotice(null)
              const token = await requestToken(username, password)
              login(token)
              setError(null)
              navigate("/tasks", {replace: true})
            } catch (err) {
              if (err instanceof Error)
                setError(err.message)
              else
                setError("Error desconocido. Intenta más tarde")
            }
          }}>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />

          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>

          <button type="submit">Submit</button>
        </form>

        <Link to="/register">Crear una cuenta</Link>

        {error !== null ? <p>Ocurrio un error : {error}</p> : <></>}

        {notice ? <p>{notice}</p> : <></>}
      </>
    )
}
