import React, { useState } from 'react';
import { Tabs, rem, Button } from '@mantine/core';
import { IconMusic, IconUser, IconHeart } from '@tabler/icons-react'; // Import heart icon
import AudioFiles from '../audio/audiofiles';
import AccountDrawer from '../drawer/accountdrawer'; // Import AccountDrawer
import FavouritesAudioFiles from '../audio/favourites'; // Import the Favourites component (assumed to exist)
import './dashboard.css'; // Import the CSS file

const Dashboard = () => {
  const [drawerOpened, setDrawerOpened] = useState(false); // State for Drawer
  const iconStyle = { width: rem(16), height: rem(16) }; // Styling for icons

  return (
    <div className="dashboard-container">
      <Tabs className="tabs-bar" defaultValue="audiofiles">
        <Tabs.List className="tabs-list">
          {/* Tab for Audio Files */}
          <Tabs.Tab value="audiofiles" leftSection={<IconMusic style={iconStyle} />}>
            Audio Files
          </Tabs.Tab>
          {/* Tab for Favourites */}
          <Tabs.Tab value="favourites" leftSection={<IconHeart style={iconStyle} />}>
            Favourites
          </Tabs.Tab>
          {/* Drawer Trigger for My Account */}
          <div className="my-account-button">
            <Button 
              variant="subtle"
              className="my-account-button"
              onClick={() => setDrawerOpened(true)} 
              style={{ padding: '10'}}
            >
              <IconUser style={iconStyle} /> My Account
            </Button>
          </div>
        </Tabs.List>

        {/* Panels render based on the selected tab */}
        <div className="tabs-panels">
          <Tabs.Panel value="audiofiles" className="tabs-panel">
            <AudioFiles />
          </Tabs.Panel>

          <Tabs.Panel value="favourites" className="tabs-panel">
            <FavouritesAudioFiles />
          </Tabs.Panel>
        </div>
      </Tabs>
      <AccountDrawer opened={drawerOpened} onClose={() => setDrawerOpened(false)} />
    </div>
  );
};

export default Dashboard;
