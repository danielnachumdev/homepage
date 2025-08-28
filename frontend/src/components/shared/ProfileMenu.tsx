import {
  Box,
  Menu,
  MenuItem,
  Typography,
  Chip,
} from '@mui/material';
import type { ChromeProfile } from '../../services';

interface ProfileMenuProps {
  anchorEl: HTMLElement | null;
  open: boolean;
  onClose: () => void;
  profiles: ChromeProfile[];
  onProfileSelect: (profile: ChromeProfile) => void;
  title?: string;
  selectedProfileId?: string;
  showActiveIndicator?: boolean;
}

export function ProfileMenu({
  anchorEl,
  open,
  onClose,
  profiles,
  onProfileSelect,
  title = 'Open with profile:',
  selectedProfileId,
  showActiveIndicator = true,
}: ProfileMenuProps) {
  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
    >
      <MenuItem disabled>
        <Typography variant="subtitle2">{title}</Typography>
      </MenuItem>
      {profiles.map(profile => (
        <MenuItem
          key={profile.id}
          onClick={() => onProfileSelect(profile)}
          selected={selectedProfileId === profile.id}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span>{profile.icon || '👤'}</span>
            <Typography>{profile.name}</Typography>
            {showActiveIndicator && profile.is_active && (
              <Chip label="Active" size="small" color="primary" />
            )}
          </Box>
        </MenuItem>
      ))}
    </Menu>
  );
}
