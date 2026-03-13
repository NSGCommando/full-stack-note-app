import './App.css';
import { Routes, Route, useNavigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import SignUp from './pages/SignUp';
import RoleBasedRouteProtector from './components/RoleBasedRouteProtector';
import { useAuthVerify } from './hooks/useAuthVerify';

function App() {
  const navigateObject = useNavigate();
  // verify any existing users and get the user object
  const {user, setUser, isVerifying} = useAuthVerify(navigateObject);
  
  if (isVerifying) {
  return <div className="loading-screen">Checking your session...</div>;
  }

  return(
    <Routes>  
      <Route path="/" element = {<LoginPage setUser={setUser}/>}/>
      {/*user? returns undefined if user doesn't exist, so user?.is_admin beceomes undefined and redirect happens*/}
      <Route path="/admin/dashboard" element = {
        <RoleBasedRouteProtector user={user} requiredRole="admin">
          <AdminDashboard user={user} setUser={setUser}/>
        </RoleBasedRouteProtector>
        }/>
      {/*we want to kick out admins from the user-dashboard, so invert the is_admin check
      In JS, (A && B) never evaluates B if A is falsy, so we guarantee user.is_admin isn't accessed unless user exists*/}
      <Route path="/user/dashboard" element = {
        <RoleBasedRouteProtector user={user} requiredRole="user">
          <UserDashboard user={user} setUser={setUser}/>
        </RoleBasedRouteProtector>
      }/>
      <Route path="/signup" element = {<SignUp/>}/>
    </Routes>
  )
 }

export default App;