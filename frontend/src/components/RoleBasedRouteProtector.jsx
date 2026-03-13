import { Navigate } from 'react-router-dom';

/**
 * Component to handle Role Based Routing
 */
function RoleBasedRouteProtector({ user, requiredRole, children }) {
  if (!user) return <Navigate to="/" replace />;
  if (requiredRole === 'admin' && !user.is_admin) {
    console.log("Non-admin kicked out");
    return <Navigate to="/" replace />;
  }
  if (requiredRole === 'user' && user.is_admin) {
    console.log("Non-user kicked out");
    return <Navigate to="/" replace />;}
  return children;
}
export default RoleBasedRouteProtector;