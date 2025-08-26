import React, { useEffect, useState } from 'react';
import { fetchDevices, fetchDeviceEvents, login } from './services';

function App() {
  const [token, setToken] = useState('');
  const [devices, setDevices] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [wsData, setWsData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = async () => {
    try {
      const res = await login(username, password);
      setToken(res.data.access_token);
      const r = await fetchDevices(res.data.access_token);
      setDevices(r.data.devices);
      setIsLoggedIn(true);
    } catch (err) {
      alert('Login failed');
    }
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/events');

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        console.log("📨 WebSocket message:", data);
        setWsData(data);

        if (data.timestamp) {
          setLastUpdate(new Date(data.timestamp * 1000).toLocaleString());
        } else {
          setLastUpdate("No timestamp available");
        }
      } catch (err) {
        console.error("❌ Error parsing WebSocket message:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
    };

    ws.onclose = () => {
      console.warn("🔌 WebSocket disconnected");
    };

    return () => ws.close();
  }, []);

  const handleSelect = (deviceId) => {
    setSelectedDevice(deviceId);
    fetchDeviceEvents(deviceId, token).then(res => setEvents(res.data));
  };

  const handleRefresh = () => {
    if (selectedDevice) {
      fetchDeviceEvents(selectedDevice, token).then(res => setEvents(res.data));
    }
  };

  if (!isLoggedIn) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <h2>Login to BDU IoT Dashboard</h2>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        /><br />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        /><br />
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h2>BDU IoT Dashboard</h2>

      {wsData && wsData.device_id && (
        <p>📡 Real-time: <b>{wsData.device_id}</b> → {wsData.temperature}°C / {wsData.humidity}%</p>
      )}
      {lastUpdate && <p>🕒 Last updated at: {lastUpdate}</p>}

      <div>
        <label>Select Device: </label>
        <select onChange={e => handleSelect(e.target.value)} value={selectedDevice}>
          <option value="">-- Select --</option>
          {devices.map(dev => <option key={dev} value={dev}>{dev}</option>)}
        </select>
        <button onClick={handleRefresh} style={{ marginLeft: '10px' }}>🔄 Refresh</button>
      </div>

      <h3>Recent Events</h3>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Temperature</th>
            <th>Humidity</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e, idx) => (
            <tr key={idx}>
              <td>{new Date(e.timestamp * 1000).toLocaleString()}</td>
              <td>{e.temperature}</td>
              <td>{e.humidity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
