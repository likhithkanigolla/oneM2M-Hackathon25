import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./store/useAuth";
import Index from "./pages/Index";
import Rooms from "./pages/Rooms";
import RoomDetails from "./pages/RoomDetails";
import Agents from "./pages/Agents";
import SLOConfig from "./pages/SLOConfig";
import LLMInsights from "./pages/LLMInsights";
import Analytics from "./pages/Analytics";
import Users from "./pages/Users";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/auth" element={isAuthenticated ? <Navigate to="/" replace /> : <Auth />} />
      <Route element={<Layout />}>
        <Route path="/" element={
          <ProtectedRoute>
            <Index />
          </ProtectedRoute>
        } />
        <Route path="/rooms" element={
          <ProtectedRoute>
            <Rooms />
          </ProtectedRoute>
        } />
        <Route path="/room/:id" element={
          <ProtectedRoute>
            <RoomDetails />
          </ProtectedRoute>
        } />
        <Route path="/agents" element={
          <ProtectedRoute>
            <Agents />
          </ProtectedRoute>
        } />
        <Route path="/slo" element={
          <ProtectedRoute>
            <SLOConfig />
          </ProtectedRoute>
        } />
        <Route path="/insights" element={
          <ProtectedRoute>
            <LLMInsights />
          </ProtectedRoute>
        } />
        <Route path="/analytics" element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        } />
        <Route path="/users" element={
          <ProtectedRoute requireAdmin={true}>
            <Users />
          </ProtectedRoute>
        } />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
