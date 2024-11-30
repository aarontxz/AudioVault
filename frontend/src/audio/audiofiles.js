import React, { useState } from 'react';
import { Container, Card, Group, Button, Table, Text, ActionIcon, FileInput } from '@mantine/core';
import { IconTrash, IconPlayerPlay } from '@tabler/icons-react';
import "./audiofiles.css";

function AudioFiles() {
  const [audioFiles, setAudioFiles] = useState([]); // List of uploaded audio files
  const [selectedFile, setSelectedFile] = useState(null); // Currently selected file for upload

  // Handle file upload
  const handleFileUpload = () => {
    if (selectedFile) {
      const newFile = {
        id: Date.now(),
        name: selectedFile.name,
        url: URL.createObjectURL(selectedFile),
      };
      setAudioFiles([...audioFiles, newFile]);
      setSelectedFile(null);
    }
  };

  // Handle file delete
  const handleDeleteFile = (id) => {
    setAudioFiles(audioFiles.filter((file) => file.id !== id));
  };

  const rows = audioFiles.map((file) => (
    <tr key={file.id}>
      <td>{file.name}</td>
      <td>
        <audio controls>
          <source src={file.url} type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
      </td>
      <td>
        <ActionIcon color="red" onClick={() => handleDeleteFile(file.id)}>
          <IconTrash />
        </ActionIcon>
      </td>
    </tr>
  ));

  return (
    <Container className="audiofiles">
      <Card shadow="sm" padding="lg" radius="md" style={{ marginBottom: '20px' }}>
        <Group position="apart" mb="xl">
          <Text align="left" size="xl" fw="700">
            Audio File Manager
          </Text>
        </Group>

        {/* File Upload */}
        <Group mb="md">
          <FileInput
            placeholder="Choose an audio file"
            accept="audio/*"
            value={selectedFile}
            onChange={(file) => setSelectedFile(file)}
          />
          <Button onClick={handleFileUpload} disabled={!selectedFile}>
            Upload
          </Button>
        </Group>

        {/* Uploaded Files Table */}
        <Table highlightOnHover>
          <thead>
            <tr>
              <th>File Name</th>
              <th>Preview</th>
              <th>Delete</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </Table>
      </Card>
    </Container>
  );
}

export default AudioFiles;
