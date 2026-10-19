import './App.css'
import { Route, Routes } from 'react-router';
import { LoginForm } from './components/LoginForm.tsx';
import TasksPage from './pages/TasksPage.tsx';
import { RegisterForm } from './components/RegisterForm.tsx';
import { ProtectedRoute } from './components/ProtectedRoute.tsx';


const App = () =>
   (
    <>
      <Routes>
        <Route path='/register' element={<RegisterForm />} />
        <Route path='/login' element={<LoginForm />} />
        <Route path='/tasks' element={
            <ProtectedRoute>
              <TasksPage />
            </ProtectedRoute>
          }/>
      </Routes>
    </>
  )

export default App
