import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent page reload
    const request_token = localStorage.getItem("token")
    const request_device_id = localStorage.getItem("device_id");
    try {
      const res = await axios.post("https://email-check-backend.onrender.com/api/login", {
        username,
        password,
      },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${request_token}`,
            "X-Device-ID": request_device_id,
          },
          withCredentials: true,
        }
      );

      const { token } = res.data;
      const { emails } = res.data;
      const { device_id } = res.data;
      const emailList: string[] = emails;
      if (token) {
        localStorage.setItem("token", token);
        localStorage.setItem("device_id", device_id);
        const query = emailList.map(email => `email=${encodeURIComponent(email)}`).join("&");
        navigate(`/dashboard?${query}`);
      } else {
        setError("No token received. Login failed.");
      }
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
        <div className="flex justify-center mb-4">
          <img src="/user.jpg" alt="User Icon" className="w-16 h-16" />
        </div>
        <h2 className="text-xl font-semibold mb-6">
          LOGIN BROTHER'S IT INBOXING CHECKER
        </h2>

        {error && (
          <div className="mb-4 text-sm text-red-600 bg-red-100 p-2 rounded">
            {error}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleLogin}>
          <div className="text-left">
            <label className="block mb-1 text-sm font-medium">Username:</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
          <div className="text-left">
            <label className="block mb-1 text-sm font-medium">Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
