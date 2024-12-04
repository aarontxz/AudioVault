import React, { useEffect, useState } from 'react';
import { Button, Table, Group, Modal, TextInput, Text, Container, ActionIcon, PasswordInput, Card, Select, ScrollArea} from '@mantine/core';
import { IconEdit, IconTrash, IconPlus } from '@tabler/icons-react';
import './manage.css';

function Manage({selectedTab}) {
  const [users, setUsers] = useState([]); 
  const [filteredUsers, setFilteredUsers] = useState([]); 
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false); 
  const [deleteConfirmation, setDeleteConfirmation] = useState(false); 
  const [selectedUser, setSelectedUser] = useState(null); 
  const [userToDelete, setUserToDelete] = useState(null); 
  const [newUser, setNewUser] = useState({ username: '', role: '', password: ''}); 
  const [message, setMessage] = useState(''); 
  const [messageType, setMessageType] = useState(''); 
  const [editmessage, setEditMessage] = useState(''); 
  const [editmessageType, setEditMessageType] = useState(''); 
  const [addmessage, setAddMessage] = useState(''); 
  const [addmessageType, setAddMessageType] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const resetState = () => {
    setUsers([]);
    setFilteredUsers([]);
    setIsAddModalOpen(false);
    setIsEditModalOpen(false);
    setDeleteConfirmation(false);
    setSelectedUser(null);
    setUserToDelete(null);
    setNewUser({ username: '', role: '', password: '' });
    setMessage('');
    setMessageType('');
    setEditMessage('');
    setEditMessageType('');
    setAddMessage('');
    setAddMessageType('');
    setSearchTerm('');
  };
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  useEffect(() => {
    if (selectedTab === 'manage users') {
      fetchUsers();
      resetState(); // Reset all state variables when the tab is selected
    }
  }, [selectedTab]);

  useEffect(() => {
    setFilteredUsers(
      users.filter((user) => user.username.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [searchTerm, users]);

  const fetchUsers = async () => {
    const token = localStorage.getItem('access_token');
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
    const token = localStorage.getItem('access_token'); 
    if (!token) {
      console.error('No token found');
      return;
    }
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newUser),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        setMessageType('success');
        setNewUser({ username: '', role: '', password: ''});
        fetchUsers(); 
        setIsAddModalOpen(false); 
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
    const token = localStorage.getItem('access_token'); // Or wherever your token is stored
    if (!token) {
      console.error('No token found');
      return;
    }
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json' ,
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(selectedUser),
      });

      if (response.ok) {
        setMessage('User updated successfully!');
        setMessageType('success');
        fetchUsers(); 
        setIsEditModalOpen(false);
      } else {
        const data = await response.json();
        setEditMessage(data.error);
        setEditMessageType('error');
      }
    } catch (error) {
      setEditMessage('An error occurred while updating the user.');
      setEditMessageType('error');
    }
  };

  const handleDeleteUser = async () => {
    const token = localStorage.getItem('access_token'); // Or wherever your token is stored
    if (!token) {
      console.error('No token found');
      return;
    }
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/users/${userToDelete.id}`,
        { method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}`},
        }
      );

      if (response.ok) {
        setMessage('User deleted successfully!');
        setMessageType('success');
        fetchUsers();
        setDeleteConfirmation(false);
      } else {
        const data = await response.json();
        setMessage(data.error);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An error occurred while deleting the user.');
      setMessageType('error');
    }
  };

  const rows = filteredUsers.map((user) => (
    <Card shadow="sm" radius="md" className = "card" key={user.id}>
      <Table style={{ tableLayout: 'fixed', width: '100%' }}>
        <tbody>
          <tr>
            <td style={{ width: '60%', textAlign: 'left', padding: '10px' }}>{user.username}</td>
            <td style={{ width: '24%' }}>{user.role}</td>
            <td style={{ width: '8%' }}>
              <ActionIcon
                className="actionicon"
                color="blue"
                onClick={() => {
                  setSelectedUser(user);
                  setIsEditModalOpen(true);
                }}
              >
                <IconEdit />
              </ActionIcon>
            </td>
            <td style={{ width: '8%' }}>
              <ActionIcon
                className="actionicon"
                color="grey"
                onClick={() => {
                  setUserToDelete(user);
                  setDeleteConfirmation(true);
                }}
              >
                <IconTrash />
              </ActionIcon>
            </td>
          </tr>
        </tbody>
      </Table>
    </Card>
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

        <Table className="headers" style={{ tableLayout: 'fixed' }}>
          <thead>
            <tr>
              <th style={{ width: '60%' }}>Username</th>
              <th style={{ width: '25%' }}>Role</th> 
              <th style={{ width: '3%' }}>Edit</th> 
              <th style={{ width: '17%' }}>Delete</th> 
            </tr>
          </thead>
        </Table>

        <ScrollArea className="scrollarea">
          <Table style={{ tableLayout: 'fixed' }}>
            <tbody>{filteredUsers.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '10px' }}>
                  No users here, remove keywords from the search bar or create more users. Try logging out and logging back in if you are suppose to see users.
                </td>
              </tr>
            ) : (
              rows
            )}</tbody>
          </Table>
        </ScrollArea>
      </Card>
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
          <Text c={editmessageType === 'success' ? 'green' : 'red'}>{editmessage}</Text>
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