import React from 'react';
import { Tabs, rem } from '@mantine/core';
import { IconMusic, IconUsers } from '@tabler/icons-react'; // Import relevant icons
import Manage from '../manage/manage'; // Import your Manage component
import AudioFiles from '../audio/audiofiles'; 
import './dashboard.css'; // Import the CSS file

const Dashboard = () => {
  const iconStyle = { width: rem(16), height: rem(16) }; // Styling for icons

  return (
    <div className="dashboard-container">
      <Tabs defaultValue="manage" className="tabs-bar">
        <Tabs.List className="tabs-list">
          {/* Tab for Manage */}
          <Tabs.Tab value="manage" leftSection={<IconUsers style={iconStyle} />}>
            Manage
          </Tabs.Tab>
          {/* Tab for Login */}
          <Tabs.Tab value="audiofiles" leftSection={<IconMusic style={iconStyle} />}>
            Audio Files
          </Tabs.Tab>
        </Tabs.List>

        {/* Panels render based on the selected tab */}
        <Tabs.Panel value="manage" className="tabs-panel">
          <Manage />
        </Tabs.Panel>

        <Tabs.Panel value="audiofiles" className="tabs-panel">
          <AudioFiles />
        </Tabs.Panel>
      </Tabs>
    </div>
  );
};

export default Dashboard;
