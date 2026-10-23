import { useState } from "react"
import { Link, useNavigate } from "react-router"
import { API_URL } from "../api/config"

async function register(email: string, password: string) {
    const params = {
      "email": email,
      "password": password
    }

    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        body: JSON.stringify(params),
        headers: {
          'Content-Type': 'application/json'
        }
    })

    if (!response.ok) {
        const error_json = await response.json()
        throw new Error(`Register error: ${response.status} - ${response.statusText} - ${error_json.detail}`, {cause: error_json })
    }
}

export function RegisterForm() {

    const [email, setEmail] = useState<string>("")
    const [password, setPassword] = useState<string>("")
    const [error, setError] = useState<string|null>(null)

    const navigate = useNavigate()

    return (
      <>
        <form className="auth-form" onSubmit={async (e) => {
            e.preventDefault()
            try {
              await register(email, password)
              setError(null)
              navigate("/login", {replace: true, state: "Usuario creado exitosamente"})
            } catch (err) {
              if (err instanceof Error)
                setError(err.message)
              else
                setError("Error desconocido. Intenta más tarde")
            }
          }}>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />

            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>

            <button type="submit">Submit</button>
        </form>

        <Link to="/login">Iniciar sesion</Link>

        {error !== null ? <p>Ocurrio un error : {error}</p> : <></>}
      </>
    )
}
