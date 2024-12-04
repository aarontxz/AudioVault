import React, { useState, useEffect } from 'react';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core'; // Import MantineProvider
import { BrowserRouter as Router, Route, Routes, Navigate} from 'react-router-dom';
import Login from './login/login';
import Dashboard from './dashboard/dashboard';
import UserDashboard from './dashboard/userdashboard';
import './App.css';
import '@mantine/notifications/styles.css';
import { jwtDecode } from "jwt-decode";


const PrivateRoute = ({ element }) => {
  const token = localStorage.getItem('access_token'); 

  // If no token exists, redirect to login
  if (!token) {
    return <Navigate to="/" />;
  }

  try {
    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    // Check if the token has expired
    if (decodedToken.exp < currentTime) {
      localStorage.removeItem('access_token'); 
      return <Navigate to="/" />; 
    }

  } catch (error) {
    localStorage.removeItem('access_token');
    return <Navigate to="/" />;
  }

  return element; 
};

const PrivateAdminRoute = ({ element }) => {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('user_role')

  if (!token) {
    return <Navigate to="/" />;
  }

  try {
    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    if (decodedToken.exp < currentTime) {
      localStorage.removeItem('access_token'); 
      return <Navigate to="/" />;
    }

    if (role !== 'admin') {
      return <Navigate to="/user" />;
    }

  } catch (error) {

    localStorage.removeItem('access_token');
    return <Navigate to="/" />;
  }

  return element; 
};


function App() {

  return (
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/admin" element={<PrivateAdminRoute element={<Dashboard />} />} />
            <Route path="/user" element={<PrivateRoute element={<UserDashboard />} />} />
          </Routes>
        </div>
      </Router>
    </MantineProvider>
  );
}

export default App;
