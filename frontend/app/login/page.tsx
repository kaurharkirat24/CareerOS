"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import toast from "react-hot-toast";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isLogin) {
        // OAuth2 Password Request Form requires x-www-form-urlencoded
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        
        const res = await api.post("/auth/token", formData);
        localStorage.setItem("token", res.data.access_token);
        toast.success("Successfully logged in!");
        router.push("/");
      } else {
        const res = await api.post("/auth/register", {
          email,
          password,
          full_name: fullName
        });
        localStorage.setItem("token", res.data.access_token);
        toast.success("Account created successfully!");
        router.push("/profile");
      }
    } catch (err) {
      toast.error(isLogin ? "Authentication failed! Check your credentials." : "Failed to create account. User might already exist.");
      console.error(err);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 p-8 glass rounded-2xl shadow-xl">
      <h2 className="text-2xl font-bold text-center mb-6 text-slate-800">
        {isLogin ? "Welcome Back to CareerOS" : "Join CareerOS"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div>
            <label className="block text-sm font-medium text-slate-700">Full Name</label>
            <input 
              type="text" 
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full p-2.5 rounded-lg border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-500" 
              required={!isLogin} 
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input 
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full p-2.5 rounded-lg border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-500" 
            required 
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input 
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full p-2.5 rounded-lg border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-500" 
            required 
          />
        </div>
        <button type="submit" className="w-full bg-indigo-600 text-white font-medium py-2.5 rounded-lg hover:bg-indigo-700 transition">
          {isLogin ? "Login" : "Sign Up"}
        </button>
      </form>
      <p className="text-center text-sm text-slate-500 mt-4 cursor-pointer hover:text-indigo-600" onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
      </p>
    </div>
  );
}
