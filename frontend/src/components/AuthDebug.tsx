import { useAuth } from '@/store/useAuth';

export const AuthDebug = () => {
  const { user, token, isAuthenticated, loading, error } = useAuth();
  
  return (
    <div className="p-4 border rounded-lg bg-muted/10">
      <h3 className="font-bold">Auth Debug:</h3>
      <p>User: {user ? `${user.username} (${user.role})` : 'null'}</p>
      <p>Token: {token ? `${token.substring(0, 20)}...` : 'null'}</p>
      <p>IsAuthenticated: {isAuthenticated.toString()}</p>
      <p>Loading: {loading.toString()}</p>
      <p>Error: {error || 'null'}</p>
    </div>
  );
};