import React, { useState, useEffect } from 'react';
import { Tabs, rem, Button, Box } from '@mantine/core';
import { IconMusic, IconUsers, IconUser, IconHeart } from '@tabler/icons-react'; 
import AudioFiles from '../audio/audiofiles';
import AccountDrawer from '../drawer/accountdrawer';
import FavouritesAudioFiles from '../audio/favourites'; 
import './dashboard.css'; 

const UserDashboard = () => {
  const currentTab = localStorage.getItem('selectedTab') || 'audiofiles';
  const [selectedTab, setSelectedTab] = useState(currentTab);
  const [drawerOpened, setDrawerOpened] = useState(false);

  const iconStyle = { width: rem(16), height: rem(16) }; 

  // Persist selectedTab to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('selectedTab', selectedTab);
  }, [selectedTab]);

  // Handle tab click to update selectedTab
  const handleTabClick = (tab) => {
    setSelectedTab(tab); // Update the state when tab is clicked
  };

  return (
    <div className="dashboard-container">
      <Tabs
        className="tabs-bar"
        value={selectedTab} // Set the current tab value
        onTabChange={(tab) => setSelectedTab(tab)} 
      >
        <Tabs.List className="tabs-list">
          {/* Leftmost Non-Clickable Tab for App Name */}
          <Box className="app-name-tab">
            AUDIOVAULT🎵🗄️
          </Box>
          {/* Tab for Audio Files */}
          <Tabs.Tab
            value="audiofiles"
            leftSection={<IconMusic style={iconStyle} />}
            onClick={() => handleTabClick('audiofiles')}
          >
            Audio Files
          </Tabs.Tab>
          {/* Tab for Favourites */}
          <Tabs.Tab
            value="favourites"
            leftSection={<IconHeart style={iconStyle} />}
            onClick={() => handleTabClick('favourites')} 
          >
            Favourites
          </Tabs.Tab>
          {/* Drawer Trigger for My Account */}
          <div className="my-account-button">
            <Button 
              variant="subtle"
              className="my-account-button"
              onClick={() => setDrawerOpened(true)} 
              style={{ padding: '10px' }}
            >
              <IconUser style={iconStyle} /> My Account
            </Button>
          </div>
        </Tabs.List>

        {/* Panels render based on the selected tab */}
        <div className="tabs-panels">
          <Tabs.Panel value="audiofiles" className="tabs-panel">
            <AudioFiles selectedTab={selectedTab} />
          </Tabs.Panel>

          <Tabs.Panel value="favourites" className="tabs-panel">
            <FavouritesAudioFiles selectedTab={selectedTab} />
          </Tabs.Panel>
        </div>
      </Tabs>
      <AccountDrawer opened={drawerOpened} onClose={() => setDrawerOpened(false)} />
    </div>
  );
};

export default UserDashboard;
