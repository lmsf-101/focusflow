import { useEffect, type ReactNode } from "react"
import { useNavigate } from "react-router"
import { useAuth } from "../auth/AuthContext"


export const ProtectedRoute = ({ children }: {children: ReactNode}) => {

  const { token } = useAuth()
    
  const navigate = useNavigate()

  useEffect(() => {
    if (token === null) {
      navigate("/login", {replace: true})
    }
  }, [navigate, token])

  return token === null ? <></> : children
}