// frontend/src/components/Login.js
import React, { useState } from 'react';
import axios from 'axios';

const Login = ({ setToken }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/token', new URLSearchParams({
        username,
        password
      }));
      setToken(res.data.access_token);
    } catch (err) {
      alert('Sai tài khoản hoặc mật khẩu');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>🔐 Đăng nhập</h2>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
};

export default Login;