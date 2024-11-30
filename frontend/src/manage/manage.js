import React, { useEffect, useState } from 'react';
import { Button, Table, Group, Modal, TextInput, Text, Container, ActionIcon, PasswordInput, Card, Select, ScrollArea} from '@mantine/core';
import { IconEdit, IconTrash, IconPlus } from '@tabler/icons-react';
import './manage.css';

function Manage() {
  const [users, setUsers] = useState([]); // State to store users
  const [filteredUsers, setFilteredUsers] = useState([]); // State to store filtered users
  const [isAddModalOpen, setIsAddModalOpen] = useState(false); // To toggle the add user modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false); // To toggle the edit user modal
  const [deleteConfirmation, setDeleteConfirmation] = useState(false); // For delete confirmation
  const [selectedUser, setSelectedUser] = useState(null); // To store the user to be edited
  const [userToDelete, setUserToDelete] = useState(null); // 
  const [newUser, setNewUser] = useState({ username: '', role: '', password: ''}); // For adding a new user
  const [message, setMessage] = useState(''); 
  const [messageType, setMessageType] = useState(''); 
  const [editmessage, setEditMessage] = useState(''); // For displaying success or error messages
  const [editmessageType, setEditMessageType] = useState(''); // To set the type of message: 'success' or 'error'
  const [addmessage, setAddMessage] = useState(''); 
  const [addmessageType, setAddMessageType] = useState('');
  const [searchTerm, setSearchTerm] = useState(''); // For searching by username

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    // Filter users based on search term
    setFilteredUsers(
      users.filter((user) => user.username.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [searchTerm, users]);

  const fetchUsers = async () => {
    const token = localStorage.getItem('access_token'); // Or wherever your token is stored
    if (!token) {
      console.error('No token found');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();
      if (response.ok) {
        setUsers(data.users);
      } else {
        console.error('Failed to fetch users:', data.error);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleAddUser = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        setMessageType('success');
        setNewUser({ username: '', role: '', password: ''});
        fetchUsers(); // Refresh the user list
        setIsAddModalOpen(false); // Close the add modal
      } else {
        const errorData = await response.json();
        setAddMessage(errorData.error);
        setAddMessageType('error');
      }
    } catch (error) {
      setAddMessage('An error occurred while creating the user.');
      setAddMessageType('error');
    }
  };

  const handleEditUser = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedUser),
      });

      if (response.ok) {
        setMessage('User updated successfully!');
        setMessageType('success');
        fetchUsers(); // Refresh the user list
        setIsEditModalOpen(false); // Close the edit modal
      } else {
        setEditMessage('Failed to update user.');
        setEditMessageType('error');
      }
    } catch (error) {
      setEditMessage('An error occurred while updating the user.');
      setEditMessageType('error');
    }
  };

  const handleDeleteUser = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/users/${userToDelete.id}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setMessage('User deleted successfully!');
        setMessageType('success');
        fetchUsers();
        setDeleteConfirmation(false); // Close confirmation modal
      } else {
        setMessage('Failed to delete user.');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An error occurred while deleting the user.');
      setMessageType('error');
    }
  };

  const rows = filteredUsers.map((user) => (
    <tr key={user.id}>
      <td>{user.username}</td>
      <td>{user.role}</td>
      <td>
        <ActionIcon
          color="blue"
          onClick={() => {
            setSelectedUser(user);
            setIsEditModalOpen(true);
          }}
        >
          <IconEdit />
        </ActionIcon>
      </td>
      <td>
        <ActionIcon
          color="red"
          onClick={() => {
            setUserToDelete(user);
            setDeleteConfirmation(true);
          }}
        >
          <IconTrash />
        </ActionIcon>
      </td>
    </tr>
  ));

  return (
    <Container className="manage">
      <Card shadow="sm" padding="lg" radius="md" style={{ marginBottom: '20px' }}>
        <Group justify="space-between" mb="xl">
          <Text align="left" size="xl" fw="700">Users Manager</Text>
          {message && (
            <Text c={messageType === 'success' ? 'green' : 'red'}>{message}</Text>
          )}
          <Button 
            onClick={() => setIsAddModalOpen(true)} 
            leftIcon={<IconPlus />} 
            color="blue"
          >
            Add User
          </Button>
        </Group>

        {/* Search Bar */}
        <TextInput
          placeholder="Search by username"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ marginBottom: '20px' }}
        />

        <Table highlightOnHover className="headers" style={{ tableLayout: 'fixed' }}>
          <thead>
            <tr>
              <th>Username</th>
              <th>Role</th>
              <th>Edit</th>
              <th>Delete</th>
            </tr>
          </thead>
        </Table>

        <ScrollArea className="scrollarea">
          <Table highlightOnHover="true" style={{ tableLayout: 'fixed' }}>
            <tbody>{rows}</tbody>
          </Table>
        </ScrollArea>
      </Card>

      {/* Modals for add, edit, and delete remain the same */}
      {/* Delete Confirmation Modal */}
      <Modal
        opened={deleteConfirmation}
        onClose={() => setDeleteConfirmation(false)}
        title="Confirm Delete"
      >
        <Text>Are you sure you want to delete this user?</Text>
        <Group position="right" mt="md">
          <Button color="gray" onClick={() => setDeleteConfirmation(false)}>
            Cancel
          </Button>
          <Button color="red" onClick={handleDeleteUser}>
            Delete
          </Button>
        </Group>
      </Modal>

      {/* Add User Modal */}
      <Modal
        opened={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add User"
      >
        {addmessage && (
          <Text c={addmessageType === 'success' ? 'green' : 'red'}>{addmessage}</Text>
        )}
        <TextInput
          label="Username"
          placeholder="Set user's username"
          value={newUser.username}
          onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
        />
        <Select
          label="Select user role"
          placeholder="member"
          data={['member', 'admin']}
          value={newUser.role}
          onChange={(value) => setNewUser({ ...newUser, role: value })}
        />
        <PasswordInput
          label="Password"
          placeholder="Set user's password"
          value={newUser.password}
          onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
        />
        <Group position="right" mt="md">
          <Button onClick={handleAddUser}>Add User</Button>
        </Group>
      </Modal>

      {/* Edit User Modal */}
      <Modal
        opened={isEditModalOpen}
        onClose={() => { setIsEditModalOpen(false); setSelectedUser(null); }}
        title="Edit User"
      >
        {editmessage && (
          <Text c={editmessageType === 'success' ? 'green' : 'red'}>{message}</Text>
        )}
        <TextInput
          label="Username"
          placeholder="Leave empty to keep unchanged."
          value={selectedUser ? selectedUser.username : ''}
          onChange={(e) => setSelectedUser({ ...selectedUser, username: e.target.value })}
        />
        <Select
          label="Select user role"
          placeholder="Leave empty to keep unchanged"
          data={['admin', 'member']}
          value={selectedUser ? selectedUser.role : ''}
          onChange={(value) => setSelectedUser({ ...selectedUser, role: value })}
        />
        <PasswordInput
          label="Password"
          placeholder="Leave empty to keep unchanged"
          value={selectedUser ? selectedUser.password : ''}
          onChange={(e) => setSelectedUser({ ...selectedUser, password: e.target.value })}
        />
        <Group position="right" mt="md">
          <Button onClick={handleEditUser}>Save Changes</Button>
        </Group>
      </Modal>
    </Container>
  );
}

export default Manage;