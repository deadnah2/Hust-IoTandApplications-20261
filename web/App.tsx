import React from "react";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
// Split imports to resolve potential QueryClient member resolution issues
import { QueryClient } from "@tanstack/react-query";
import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ROUTES } from "./constants";

// Initialize QueryClient for the app
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const theme = createTheme({
  palette: {
    primary: {
      main: "#2563eb", // blue-600
    },
    background: {
      default: "#f8fafc",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    button: {
      textTransform: "none",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
        styleOverrides: {
            rounded: {
                borderRadius: 12
            }
        }
    }
  },
});

const PrivateRoute = ({ children }: React.PropsWithChildren) => {
  const token = localStorage.getItem("id_token");
  return token ? <>{children}</> : <Navigate to={ROUTES.LOGIN} />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <HashRouter>
          <Routes>
            <Route path={ROUTES.LOGIN} element={<Login />} />
            <Route
              path={ROUTES.APP}
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to={ROUTES.LOGIN} />} />
          </Routes>
        </HashRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
