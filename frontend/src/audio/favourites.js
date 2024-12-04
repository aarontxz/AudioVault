import React, { useState, useEffect } from 'react';
import { Container, Card, Group, Table, Text, ActionIcon, TextInput, ScrollArea } from '@mantine/core';
import { IconTrash, IconHeart, IconHeartFilled } from '@tabler/icons-react';
import "./audiofiles.css";

function FavouriteAudioFiles({ selectedTab }) {
  const [audioFiles, setAudioFiles] = useState([]);
  const [filteredAudioFiles, setFilteredAudioFiles] = useState([]); 
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [searchQuery, setSearchQuery] = useState(''); 


  // Fetch audio files from the backend
  const fetchAudioFiles = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/audiofiles/favourites`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Raw Response Data:', data);
        // Map the response to include audio file details and decoded content (Base64 to data URL)
        const formattedAudioFiles = (data.audiofiles || []).map((file) => ({
          ...file,
          liked: file.liked || false, // Add liked property if it doesn't exist
          audioDataUrl: file.file_content
            ? `data:audio/mpeg;base64,${file.file_content}`  // Assuming it's an MP3 file
            : file.file_url, // Fallback to the external URL if no Base64 content
        }));

        setAudioFiles(formattedAudioFiles);
        setFilteredAudioFiles(formattedAudioFiles); // Set filtered files initially
      } else {
        console.error('Failed to fetch audio files:', data.error);
      }
    } catch (error) {
      console.error('Error fetching audio files:', error);
    }
  };

  // Handle file delete
  const handleDeleteFile = async (id) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      return;
    }
  
    // Add a confirmation step before proceeding with the delete
    const confirmDelete = window.confirm('Are you sure you want to delete this file?');
  
    if (confirmDelete) {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/audiofiles/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
  
        if (response.ok) {
          setMessage('File deleted successfully!');
          setMessageType('success');
          fetchAudioFiles();
        } else {
          const data = await response.json();
          setMessage(data.error);
          setMessageType('error');
        }
      } catch (error) {
        setMessage('An error occurred while deleting the file.');
        setMessageType('error');
      }
    }
  };
  

  // Handle file like
  const handleLikeFile = async (id) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      return;
    }

    const updatedAudioFiles = audioFiles.map((file) => {
      if (file.id === id) {
        const newLikedState = !file.liked;
        return { ...file, liked: newLikedState };
      }
      return file;
    });

    setAudioFiles(updatedAudioFiles);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/audiofiles/${id}/like`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ liked: updatedAudioFiles.find(file => file.id === id).liked }),
      });

      if (!response.ok) {
        console.error('Failed to update liked status');
      }
      fetchAudioFiles();
    } catch (error) {
      console.error('Error liking the file:', error);
    }
  };

  // Handle search input change
  const handleSearch = (e) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);

    if (query) {
      const filteredFiles = audioFiles.filter((file) =>
        file.file_name.toLowerCase().includes(query)
      );
      setFilteredAudioFiles(filteredFiles);
    } else {
      setFilteredAudioFiles(audioFiles); // Show all files when no search query
    }
  };

  const rows = filteredAudioFiles.map((file) => (
    <Card shadow="sm" radius="md" className = "card" key={file.id}>
      <Table style={{ tableLayout: 'fixed', width: '100%' }}>
        <tr key={file.id}>
          <td style={{ width: '30%' }}>{file.file_name}</td> 
          <td style={{ width: '59%' }}>
          <audio controls className="audio-player">
            <source src={file.audioDataUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
          </td> 
          <td style={{ width: '6%' }}>
            <ActionIcon
              className='actionicon'
              color={file.liked ? "red" : "gray"}
              onClick={() => handleLikeFile(file.id)}
            >
              {file.liked ? <IconHeartFilled /> : <IconHeart />}
            </ActionIcon>
          </td> 
          <td style={{ width: '5%' }}>
            <ActionIcon className='actionicon' color="grey" onClick={() => handleDeleteFile(file.id)}>
              <IconTrash />
            </ActionIcon>
          </td> 
        </tr>
      </Table>
    </Card>
  ));

  useEffect(() => {
    if (selectedTab === 'favourites') {
      fetchAudioFiles();
      setMessage('');
      setMessageType('');
    }
  }, [selectedTab]); // Fetch audio files when the tab changes


  return (
    <Container className="audiofiles">
      <Card shadow="sm" padding="lg" radius="md" style={{ marginBottom: '20px' }}>
        <Group position="apart" mb="xl">
          <Text align="left" size="xl" fw="700">
            Favourite Audio Files
          </Text>
          {message && (
            <Text c={messageType === 'error' ? 'red' : 'green'}>{message}</Text>
          )}
        </Group>
        {/* Search Bar */}
        <TextInput
          placeholder="Type here to filter audio files below by keyword"
          value={searchQuery}
          onChange={handleSearch}
          mb="md"
        />

        <Table className="headers" style={{ tableLayout: 'fixed' }}>
          <thead>
            <tr>
              <th style={{ width: '32%' }}>File Name</th> {/* 50% width for the header */}
              <th style={{ width: '56%' }}>Preview</th>   {/* 30% width for the header */}
              <th style={{ width: '2%' }}>Like</th>      {/* 10% width for the header */}
              <th style={{ width: '10%' }}>Delete</th>    {/* 10% width for the header */}
            </tr>
          </thead>
        </Table>

        <ScrollArea className="scrollarea">
          <Table style={{ tableLayout: 'fixed' }}>
            <tbody>{filteredAudioFiles.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: '10px' }}>
                  No favourite audio files here, favourite more audio files or remove keywords from the search bar
                </td>
              </tr>
            ) : (
              rows
            )}</tbody>
          </Table>
        </ScrollArea>
      </Card>
    </Container>
  );
}

export default FavouriteAudioFiles;
