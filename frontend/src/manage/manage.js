import React, { useEffect, useState } from 'react';
import { Button, Table, Group, Modal, TextInput, Text, Container, ActionIcon } from '@mantine/core';
import { IconEdit, IconTrash, IconPlus } from '@tabler/icons-react';
import './manage.css';

function Manage() {
  const [users, setUsers] = useState([]); // State to store users
  const [isEditModalOpen, setIsEditModalOpen] = useState(false); // To toggle the edit modal
  const [selectedUser, setSelectedUser] = useState(null); // To store the user to be edited
  const [newUser, setNewUser] = useState({ username: '', password: '' }); // For adding a new user
  const [message, setMessage] = useState(''); // For displaying success or error messages


  // Fetch users from the backend
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    // Call your API to get the list of users (assuming you have a GET endpoint for this)
    const response = await fetch('/api/users');
    const data = await response.json();
    setUsers(data);
  };


  const handleAddUser = async () => {
    try {
      // Send a POST request to create a new user
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);  // Show the success message returned from the backend
        setNewUser({ username: '', password: '', files: [] }); // Reset form after successful user creation
      } else {
        const errorData = await response.json();
        setMessage(errorData.error);  // Show the error message if user creation fails
      }
    } catch (error) {
      console.error('Error creating user:', error);
      console.log(`${process.env.REACT_APP_BACKEND_URL}/users`)
      setMessage('An error occurred while creating the user.');
    }
  };

  const handleEditUser = async () => {
    // Update the user data
    const response = await fetch(`/api/users/${selectedUser.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedUser),
    });
    if (response.ok) {
      fetchUsers(); // Refresh the user list
      setIsEditModalOpen(false); // Close the modal
    }
  };

  const handleDeleteUser = async (id) => {
    // Delete the user
    const response = await fetch(`/api/users/${id}`, {
      method: 'DELETE',
    });
    if (response.ok) {
      fetchUsers(); // Refresh the user list
    }
  };

  return (
    <Container>
      <Group position="apart" mb="xl">
        <Text align="left" size="xl">Manage Users</Text>
        <Button onClick={() => setIsEditModalOpen(true)} leftIcon={<IconPlus />} color="blue">Add User</Button>
      </Group>
      {message && <Text color="green">{message}</Text>} {/* Show message (success or error) */}
      <Table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Password</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.password}</td>
              <td>
                <Group spacing="xs">
                  <ActionIcon onClick={() => { setSelectedUser(user); setIsEditModalOpen(true); }}>
                    <IconEdit />
                  </ActionIcon>
                  <ActionIcon onClick={() => handleDeleteUser(user.id)}>
                    <IconTrash />
                  </ActionIcon>
                </Group>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal
        opened={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title={selectedUser ? 'Edit User' : 'Add User'}
      >
        <TextInput
          label="Username"
          placeholder="Enter username"
          value={selectedUser ? selectedUser.username : newUser.username}
          onChange={(e) => selectedUser ? setSelectedUser({ ...selectedUser, username: e.target.value }) : setNewUser({ ...newUser, username: e.target.value })}
        />
        <TextInput
          label="Password"
          placeholder="Enter password"
          value={selectedUser ? selectedUser.password : newUser.password}
          onChange={(e) => selectedUser ? setSelectedUser({ ...selectedUser, password: e.target.value }) : setNewUser({ ...newUser, password: e.target.value })}
        />
        <Group position="right" mt="md">
          <Button onClick={selectedUser ? handleEditUser : handleAddUser}>
            {selectedUser ? 'Save Changes' : 'Add User'}
          </Button>
        </Group>
      </Modal>
    </Container>
  );
}

export default Manage;
