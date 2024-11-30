import React, { useState, useEffect } from 'react';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core'; // Import MantineProvider
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Routes, Navigate} from 'react-router-dom';
import Login from './login/login';
import Dashboard from './dashboard/dashboard';
import AudioFiles from './audio/audiofiles';
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
      return <Navigate to="/audiofiles" />;
    }

  } catch (error) {
    // If token decoding fails or is invalid, remove it and redirect to login
    localStorage.removeItem('access_token');
    return <Navigate to="/" />;
  }

  return element; // If token is valid and user is admin, render the requested route
};


function App() {
  // State to store the response from the backend
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/home`)
      .then(response => response.json())
      .then(data => setMessage(data.message)) // Set the message state with the response
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/dashboard" element={<PrivateAdminRoute element={<Dashboard />} />} />
            <Route path="/audiofiles" element={<PrivateRoute element={<AudioFiles />} />} />
          </Routes>
        </div>
      </Router>
    </MantineProvider>
  );
}

export default App;
