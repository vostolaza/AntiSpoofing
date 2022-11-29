import {useState} from 'react';
import './App.css';
import SignUp from './pages/SignUp/SingUp';
import Login from './pages/Login/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserContext } from "./utils/Security/UserContext";
import PrivateRoute from './utils/Security/PrivateRoute';
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <UserContext.Provider value={{user, setUser, loading, setLoading}}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path='/' element={<Login />} />
            <Route path="/signup" element={<SignUp/>} />
            <Route path="/dashboard" element={
               <PrivateRoute component={Dashboard} />}
            />
          </Routes>
        </BrowserRouter>
      </div>
    </UserContext.Provider>
  );
}

export default App;
