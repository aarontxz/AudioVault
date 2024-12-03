import React, { useState } from 'react';
import { Drawer, Button, TextInput, PasswordInput, Group, Text, Modal } from '@mantine/core';
import { IconLogout } from '@tabler/icons-react';
import './accountdrawer.css'; // Import the CSS file

const AccountDrawer = ({ opened, onClose }) => {
  const [newUsername, setNewUsername] = useState(''); // Store new username
  const [newPassword, setNewPassword] = useState(''); // Store new password
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [showConfirmUsername, setShowConfirmUsername] = useState(false); // Show confirmation for username change
  const [showConfirmPassword, setShowConfirmPassword] = useState(false); // Show confirmation for password change
  const username = localStorage.getItem('username')

  const handleEditUsername = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users/username`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ username: newUsername }),
      });

      if (response.ok) {
        setMessage('Username updated successfully!');
        setMessageType('success');
        window.location.reload();
      } else {
        const errorData = await response.json();
        setMessage(errorData.error);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An error occurred while updating the username.');
      setMessageType('error');
    }
  };

  const handleEditPassword = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users/password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ password: newPassword }),
      });

      if (response.ok) {
        setMessage('Password updated successfully!');
        setMessageType('success');
        setShowConfirmPassword(false);
      } else {
        const errorData = await response.json();
        setMessage(errorData.error);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An error occurred while updating the password.');
      setMessageType('error');
    }
  };

  const handleLogout = () => {
    // Clear authentication token from localStorage
    localStorage.clear();
    window.location.reload();
  };

  return (
    <Drawer opened={opened} onClose={onClose} position="right" padding="md" size="md">
      {/* Display the message after actions */}
      {message && <Text c={messageType === 'success' ? 'green' : 'red'}>{message}</Text>}
      <Text style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
        Hi, {username}! 👋
      </Text>
      {/* Username edit */}
      <Text style={{ fontSize: '1rem', fontWeight: 'normal', color: '#555', lineHeight: '1.5' }}>
        Here, you can update your username or password, or log out of your account.
      </Text>
      <TextInput
        label="New Username"
        placeholder="Enter new username"
        value={newUsername}
        onChange={(e) => setNewUsername(e.target.value)}
        style={{ marginBottom: '15px' }}
      />
      <Button onClick={() => setShowConfirmUsername(true)} className="account-drawer-button">
        Change Username
      </Button>

      {/* Password edit */}
      <PasswordInput
        label="New Password"
        placeholder="Enter new password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        style={{ marginBottom: '15px' }}
      />
      <Button onClick={() => setShowConfirmPassword(true)} className="account-drawer-button">
        Change Password
      </Button>

      {/* Logout Button */}
      <Group position="center" style={{ marginTop: '20px' }}>
        <Button color="grey" leftIcon={<IconLogout />} onClick={handleLogout} className="account-drawer-button">
          Logout
        </Button>
      </Group>

      {/* Confirmation Modals */}
      <Modal
        opened={showConfirmUsername}
        onClose={() => setShowConfirmUsername(false)}
        title="Confirm Username Change"
      >
        <Text>Are you sure you want to change your username to "{newUsername}"?</Text>
        <Group position="center" style={{ marginTop: '20px' }}>
          <Button color="green" onClick={handleEditUsername}>Yes, Change Username</Button>
          <Button color="red" onClick={() => setShowConfirmUsername(false)}>Cancel</Button>
        </Group>
      </Modal>

      <Modal
        opened={showConfirmPassword}
        onClose={() => setShowConfirmPassword(false)}
        title="Confirm Password Change"
      >
        <Text>Are you sure you want to change your password?</Text>
        <Group position="center" style={{ marginTop: '20px' }}>
          <Button color="green" onClick={handleEditPassword}>Yes, Change Password</Button>
          <Button color="red" onClick={() => setShowConfirmPassword(false)}>Cancel</Button>
        </Group>
      </Modal>
    </Drawer>
  );
};

export default AccountDrawer;
