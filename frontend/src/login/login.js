import React from 'react';
import { Container, Paper, Title, TextInput, PasswordInput, Button } from '@mantine/core';
import './login.css';

function Login() {
  return (
    <div className="login-wrapper">
      <Container size={420} my={40}>
        <Paper radius="md" padding="xl" withBorder className="login-box">
          <Title align="center" className="login-title">
            Log in to AudioVault
          </Title>

          <form className="login-form">
            <TextInput
              label="Username"
              placeholder="you@example.com"
              required
              className="input-field"
            />
            <TextInput
              label="Password"
              placeholder="password"
              required
              className="input-field"
            />
            <Button type="submit" className="submit-button">
              Sign In
            </Button>
          </form>
        </Paper>
      </Container>
    </div>
  );
}

export default Login;
