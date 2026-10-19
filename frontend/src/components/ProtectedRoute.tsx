import { useEffect, type ReactNode } from "react"
import { useNavigate } from "react-router"


export const ProtectedRoute = ({ children }: {children: ReactNode}) => {
    
  const navigate = useNavigate()
  const token = localStorage.getItem('token')

  useEffect(() => {
    if (token === null) {
      navigate("/login", {replace: true})
    }
  }, [navigate, token])

  return token === null ? <></> : children
}