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
  const token = localStorage.getItem('access_token'); // Retrieve the token from localStorage

  // If no token exists, redirect to login
  if (!token) {
    return <Navigate to="/" />;
  }

  try {
    // Decode the token
    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000; // Get the current time in seconds

    // Check if the token has expired
    if (decodedToken.exp < currentTime) {
      localStorage.removeItem('access_token'); // Remove expired token from localStorage
      return <Navigate to="/" />; // Redirect to login page
    }

  } catch (error) {
    // If token decoding fails or is invalid, remove it and redirect to login
    localStorage.removeItem('access_token');
    return <Navigate to="/" />;
  }

  return element; // If token is valid, render the requested route
};

const PrivateAdminRoute = ({ element }) => {
  const token = localStorage.getItem('access_token'); // Retrieve the token from localStorage
  const role = localStorage.getItem('user_role')

  // If no token exists, redirect to login
  if (!token) {
    return <Navigate to="/" />;
  }

  try {
    // Decode the token
    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000; // Get the current time in seconds

    // Check if the token has expired
    if (decodedToken.exp < currentTime) {
      localStorage.removeItem('access_token'); // Remove expired token from localStorage
      return <Navigate to="/" />; // Redirect to login page
    }

    // Check if the user role is admin
    if (role !== 'admin') {
      return <Navigate to="/user" />;
    }

  } catch (error) {
    // If token decoding fails or is invalid, remove it and redirect to login
    localStorage.removeItem('access_token');
    return <Navigate to="/" />;
  }

  return element; // If token is valid and user is admin, render the requested route
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
