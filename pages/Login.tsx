import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { TextField, Button, Paper, Typography, Tabs, Tab, Box, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { loginSchema, registerSchema } from "../types";
import { api } from "../services/api";
import { ROUTES } from "../constants";

export const Login = () => {
  const [tab, setTab] = useState(0);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: api.auth.login,
    onSuccess: (data) => {
      localStorage.setItem("id_token", data.id_token);
      navigate(ROUTES.APP);
    },
    onError: (err: any) => setError(err.message || "Login failed"),
  });

  const registerMutation = useMutation({
    mutationFn: api.auth.register,
    onSuccess: () => {
      setTab(0);
      setError(null);
      alert("Registration successful! Please login.");
    },
    onError: (err: any) => setError(err.message || "Registration failed"),
  });

  const { register: registerLogin, handleSubmit: handleLoginSubmit, formState: { errors: loginErrors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const { register: registerReg, handleSubmit: handleRegSubmit, formState: { errors: regErrors } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onLogin = (data: any) => loginMutation.mutate(data);
  const onRegister = (data: any) => registerMutation.mutate(data);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Paper className="w-full max-w-md p-6 rounded-2xl shadow-xl">
        <Typography variant="h4" className="text-center font-bold text-blue-600 mb-6">
          SmartHome
        </Typography>

        <Tabs value={tab} onChange={(_, v) => setTab(v)} centered className="mb-6">
          <Tab label="Login" />
          <Tab label="Register" />
        </Tabs>

        {error && <Alert severity="error" className="mb-4">{error}</Alert>}

        {tab === 0 ? (
          <form onSubmit={handleLoginSubmit(onLogin)} className="space-y-4">
            <TextField
              fullWidth
              label="Username"
              {...registerLogin("username")}
              error={!!loginErrors.username}
              helperText={loginErrors.username?.message as string}
            />
            <TextField
              fullWidth
              type="password"
              label="Password"
              {...registerLogin("password")}
              error={!!loginErrors.password}
              helperText={loginErrors.password?.message as string}
            />
            <Button
                fullWidth
                variant="contained"
                size="large"
                type="submit"
                disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? "Logging in..." : "Login"}
            </Button>
            <div className="text-center text-xs text-gray-400">
                Hint: admin / admin
            </div>
          </form>
        ) : (
          <form onSubmit={handleRegSubmit(onRegister)} className="space-y-4">
            <TextField
              fullWidth
              label="Username"
              {...registerReg("login")}
              error={!!regErrors.login}
              helperText={regErrors.login?.message as string}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              {...registerReg("email")}
              error={!!regErrors.email}
              helperText={regErrors.email?.message as string}
            />
            <TextField
              fullWidth
              type="password"
              label="Password"
              {...registerReg("password")}
              error={!!regErrors.password}
              helperText={regErrors.password?.message as string}
            />
            <Button fullWidth variant="contained" size="large" type="submit">
              Register
            </Button>
          </form>
        )}
      </Paper>
    </div>
  );
};
