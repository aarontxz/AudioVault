import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Paper, Title, Text, TextInput, PasswordInput, Button } from '@mantine/core';
import '@mantine/notifications/styles.css';
import './login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);  
  const navigate = useNavigate(); 

  const handleSubmit = async (e) => {
    e.preventDefault();  

    setLoading(true);
    setError(null); 

    const payload = {
      username,
      password,
    };

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

    
      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.error) {
          setError(errorData.error);
        }
        throw new Error(errorData.error || 'Login failed. Please try again.');
      }

      const data = await response.json();


      const { access_token, refresh_token, user_id, user_role} = data;

      // Save the tokens securely (e.g., to localStorage)
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user_id', user_id)
      localStorage.setItem('user_role', user_role)
      localStorage.setItem('username', username)

      if (user_role === 'admin') {
        console.log('Login successful:', data);
        navigate('/admin');
      } else {
        navigate('/user');
      }
    } catch (error) {
      console.error('Error during login:', error);
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="login-wrapper">
      <Container size={420} my={40}>
        <Paper radius="md" padding="xl" withBorder className="login-box">
          <Title align="center" className="login-title">
            Welcome to AudioVault 🎵🗄️
          </Title>
          <Text c="red">{error}</Text>
          <form className="login-form" onSubmit={handleSubmit}>
            <TextInput
              label="Username"
              placeholder="username"
              required
              className="input-field"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <PasswordInput
              label="Password"
              placeholder="password"
              required
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" className="submit-button" loading={loading}>
              Sign In
            </Button>
          </form>
        </Paper>
      </Container>
    </div>
  );
}

export default Login;
