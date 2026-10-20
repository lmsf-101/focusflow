import { createContext, useContext, useState, type ReactNode } from "react";

type AuthContextValue = {
  token: string | null
  login: (token: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({children} : {children: ReactNode}) {
  const [token, setToken] = useState<string|null>(() => 
    localStorage.getItem("token")
  )

  function login(token: string) {
      setToken(token)
      localStorage.setItem("token", token)
    }

  function logout() {
    setToken(null)
    localStorage.removeItem("token")
  }

  return <AuthContext value={{token, login, logout }}>{children}</AuthContext>

}

export function useAuth() {
  const context = useContext(AuthContext)

  if (context === null)
    throw new Error("useAuth must be inside of a AuthProvider")

  return context
}
