export interface ChromeProfile {
  id: string;
  name: string;
  icon?: string;
  isActive?: boolean;
}

export interface LinkItem {
  id: string;
  title: string;
  url: string;
  description?: string;
  icon?: string;
  category: string;
  tags?: string[];
}

export interface Section {
  id: string;
  title: string;
  description?: string;
  links: LinkItem[];
  isCollapsible?: boolean;
  isCollapsed?: boolean;
}

export interface HomepageData {
  sections: Section[];
  chromeProfiles: ChromeProfile[];
}
