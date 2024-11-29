import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Login from './login/login';
import Manage from './manage/manage'
import { MantineProvider } from '@mantine/core'; // Import MantineProvider

function App() {
  // State to store the response from the backend
  const [message, setMessage] = useState('');

  useEffect(() => {
    console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL); // Log the URL being used
    fetch(`${process.env.REACT_APP_BACKEND_URL}/home`)
      .then(response => response.json())
      .then(data => setMessage(data.message)) // Set the message state with the response
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    // Wrap your entire app in the MantineProvider
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<div><h1>{message}</h1><h1>{"helloooo3"}</h1></div>} />
            <Route path="/login" element={<Login />} />
            <Route path="/manage" element={<Manage />} />
          </Routes>
        </div>
      </Router>
    </MantineProvider>
  );
}

export default App;
