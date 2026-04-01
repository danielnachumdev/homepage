import type { LinkData } from '../types/link';

const GITHUB_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23000"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>';
const GITHUB_SVG_FALLBACK = '/src/data/github-142-svgrepo-com.svg';
export const GITHUB_LINK: LinkData = {
    title: 'danielnachumdev',
    icon: [
        // 'https://github.com/favicon.ico', // correct but low res
        GITHUB_SVG,
        GITHUB_SVG_FALLBACK
    ],
    description: 'View my code repositories and projects',
    url: 'https://github.com/danielnachumdev?tab=repositories'
};

const GMAIL_SVG_FALLBACK = '/src/data/gmail-svgrepo-com.svg';
export const GMAIL_LINK: LinkData = {
    title: 'Gmail',
    icon: [
        'https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico',
        GMAIL_SVG_FALLBACK
    ],
    description: 'Email service by Google',
    url: 'https://mail.google.com/',
    chromeProfileEnabled: true,
};

const GOOGLE_CALENDAR_SVG_FALLBACK = '/src/data/google-calendar-svgrepo-com.svg';
export const GOOGLE_CALENDAR_LINK: LinkData = {
    title: 'Google Calendar',
    icon: [
        GOOGLE_CALENDAR_SVG_FALLBACK
    ],
    description: 'Calendar and scheduling by Google',
    url: 'https://calendar.google.com/'
};

const GOOGLE_DRIVE_SVG_FALLBACK = '/src/data/drive-color-svgrepo-com.svg';
export const GOOGLE_DRIVE_LINK: LinkData = {
    title: 'Google Drive',
    icon: [
        'https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_32dp.png',
        GOOGLE_DRIVE_SVG_FALLBACK
    ],
    description: 'Cloud storage and files by Google',
    url: 'https://drive.google.com/',
    chromeProfileEnabled: true,
};

const GLZ_BRAND_SVG = '/src/data/glz-brand.svg';
const RADIO_WAVES_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%231976d2"><path d="M3.24 6.15C2.51 6.43 2 7.17 2 8v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2H8.3l7.43-3c.56-.23.84-.89.61-1.45-.21-.55-.85-.83-1.45-.62L3.24 6.15zM7 15c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm5-2c0 2.76-2.24 5-5 5s-5-2.24-5-5h2c0 1.66 1.34 3 3 3s3-1.34 3-3h2zm4 0c0 4.42-3.58 8-8 8v-2c3.31 0 6-2.69 6-6h2zm4 0c0 6.63-5.37 12-12 12v-2c5.52 0 10-4.48 10-10h2z"/></svg>';
export const GALGALATZ_LINK: LinkData = {
    title: 'גלגלצ',
    icon: [GLZ_BRAND_SVG, RADIO_WAVES_SVG],
    description: 'Israeli radio – Galgalatz (GLGLZ) live stream and site',
    url: 'https://glz.co.il/%D7%92%D7%9C%D7%92%D7%9C%D7%A6',
    addon: {
        type: 'audioVisualizer',
        streamUrl: 'https://glzwizzlv.bynetcdn.com/glglz_mp3?awCollectionId=misc&awEpisodeId=glglz',
        mimeType: 'audio/mpeg',
        modeInline: 'waveform',
        modeFullscreen: 'radialOverSpectrogram',
        frequencyLogBase: 2,
        spectrogramOpacityCurve: (x) => x ** 4,
        spectrogramMaxOpacity: 1,
        accentColor: '#7cf7c3',
    },
};

export const PYPI_MANAGE_LINK: LinkData = {
    title: 'PyPI Manage',
    icon: 'https://pypi.org/static/images/logo-small.8998e9d1.svg',
    description: 'Manage Python packages on PyPI',
    url: 'https://pypi.org/manage/projects/'
};

const LOCALHOST_SVG_WHITE_BG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="4" fill="white"/><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" fill="%23007acc"/></svg>';

/** Full link objects reused as Localhost sublinks (not listed in `links` on their own). */
export const LOCALHOST_3000_LINK: LinkData = {
    title: 'Localhost:3000',
    icon: LOCALHOST_SVG_WHITE_BG,
    description: 'Local development server on port 3000',
    url: 'http://localhost:3000',
};

export const LOCALHOST_8000_LINK: LinkData = {
    title: 'Localhost:8000',
    icon: LOCALHOST_SVG_WHITE_BG,
    description: 'Local development server on port 8000',
    url: 'http://localhost:8000',
};

export const LOCALHOST_5173_LINK: LinkData = {
    title: 'Localhost:5173',
    icon: LOCALHOST_SVG_WHITE_BG,
    description: 'Vite development server on port 5173',
    url: 'http://localhost:5173',
};

export const LOCALHOST_BUNDLE_LINK: LinkData = {
    title: 'Localhost',
    icon: LOCALHOST_SVG_WHITE_BG,
    description: 'Common local development ports (Vite, app, API)',
    url: LOCALHOST_5173_LINK.url,
    addon: {
        type: 'sublinks',
        items: [LOCALHOST_5173_LINK, LOCALHOST_3000_LINK, LOCALHOST_8000_LINK],
    },
};

export const CHATGPT_LINK: LinkData = {
    title: 'ChatGPT',
    icon: 'https://chatgpt.com/favicon.ico',
    description: 'AI-powered conversational assistant',
    url: 'https://chatgpt.com/'
};

const AWS_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 29 17" fill="%23FF9900"><path d="M8.38 6.17a2.6 2.6 0 00.11.83c.08.232.18.456.3.67a.4.4 0 01.07.21.36.36 0 01-.18.28l-.59.39a.43.43 0 01-.24.08.38.38 0 01-.28-.13 2.38 2.38 0 01-.34-.43c-.09-.16-.18-.34-.28-.55a3.44 3.44 0 01-2.74 1.29 2.54 2.54 0 01-1.86-.67 2.36 2.36 0 01-.68-1.79 2.43 2.43 0 01.84-1.92 3.43 3.43 0 012.29-.72 6.75 6.75 0 011 .07c.35.05.7.12 1.07.2V3.3a2.06 2.06 0 00-.44-1.49 2.12 2.12 0 00-1.52-.43 4.4 4.4 0 00-1 .12 6.85 6.85 0 00-1 .32l-.33.12h-.14c-.14 0-.2-.1-.2-.29v-.46A.62.62 0 012.3.87a.78.78 0 01.27-.2A6 6 0 013.74.25 5.7 5.7 0 015.19.07a3.37 3.37 0 012.44.76 3 3 0 01.77 2.29l-.02 3.05zM4.6 7.59a3 3 0 001-.17 2 2 0 00.88-.6 1.36 1.36 0 00.32-.59 3.18 3.18 0 00.09-.81V5A7.52 7.52 0 006 4.87h-.88a2.13 2.13 0 00-1.38.37 1.3 1.3 0 00-.46 1.08 1.3 1.3 0 00.34 1c.278.216.63.313.98.27zm7.49 1a.56.56 0 01-.36-.09.73.73 0 01-.2-.37L9.35.93a1.39 1.39 0 01-.08-.38c0-.15.07-.23.22-.23h.92a.56.56 0 01.36.09.74.74 0 01.19.37L12.53 7 14 .79a.61.61 0 01.18-.37.59.59 0 01.37-.09h.75a.62.62 0 01.38.09.74.74 0 01.18.37L17.31 7 18.92.76a.74.74 0 01.19-.37.56.56 0 01.36-.09h.87a.21.21 0 01.23.23 1 1 0 010 .15s0 .13-.06.23l-2.26 7.2a.74.74 0 01-.19.37.6.6 0 01-.36.09h-.8a.53.53 0 01-.37-.1.64.64 0 01-.18-.37l-1.45-6-1.44 6a.64.64 0 01-.18.37.55.55 0 01-.37.1l-.82.02zm12 .24a6.29 6.29 0 01-1.44-.16 4.21 4.21 0 01-1.07-.37.69.69 0 01-.29-.26.66.66 0 01-.06-.27V7.3c0-.19.07-.29.21-.29a.57.57 0 01.18 0l.23.1c.32.143.656.25 1 .32.365.08.737.12 1.11.12a2.47 2.47 0 001.36-.31 1 1 0 00.48-.88.88.88 0 00-.25-.65 2.29 2.29 0 00-.94-.49l-1.35-.43a2.83 2.83 0 01-1.49-.94 2.24 2.24 0 01-.47-1.36 2 2 0 01.25-1c.167-.3.395-.563.67-.77a3 3 0 011-.48A4.1 4.1 0 0124.4.08a4.4 4.4 0 01.62 0l.61.1.53.15.39.16c.105.062.2.14.28.23a.57.57 0 01.08.31v.44c0 .2-.07.3-.21.3a.92.92 0 01-.36-.12 4.35 4.35 0 00-1.8-.36 2.51 2.51 0 00-1.24.26.92.92 0 00-.44.84c0 .249.1.488.28.66.295.236.635.41 1 .51l1.32.42a2.88 2.88 0 011.44.9 2.1 2.1 0 01.43 1.31 2.38 2.38 0 01-.24 1.08 2.34 2.34 0 01-.68.82 3 3 0 01-1 .53 4.59 4.59 0 01-1.35.22l.03-.01z"/><path d="M25.82 13.43a20.07 20.07 0 01-11.35 3.47A20.54 20.54 0 01.61 11.62c-.29-.26 0-.62.32-.42a27.81 27.81 0 0013.86 3.68 27.54 27.54 0 0010.58-2.16c.52-.22.96.34.45.71z"/><path d="M27.1 12c-.4-.51-2.6-.24-3.59-.12-.3 0-.34-.23-.07-.42 1.75-1.23 4.63-.88 5-.46.37.42-.09 3.3-1.74 4.68-.25.21-.49.09-.38-.18.34-.95 1.17-3.02.78-3.5z"/></svg>';

export const AWS_CONSOLE_LINK: LinkData = {
    title: 'AWS Console',
    icon: [
        AWS_SVG,
        'https://console.aws.amazon.com/favicon.ico',
    ],
    description: 'Amazon Web Services management console',
    url: 'https://console.aws.amazon.com'
};

const GCP_CONSOLE_ICON = '/src/data/gcp-console.svg';
const CLOUD_RUN_ICON = '/src/data/cloud-run.svg';
const CLOUD_STORAGE_ICON = '/src/data/cloud-storage.svg';
const GCP_BILLING_ICON_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" data-icon-name="billingSectionIcon" viewBox="0 0 24 24" width="24" height="24" fill="%231976d2" fill-rule="evenodd" aria-hidden="true"><path d="M3 7h9v2H3z" opacity=".4"/><path d="M12 7h9v2h-9z" opacity=".3"/><path d="M5 11h14v2H5z" opacity=".6"/><path d="M4 5a1 1 0 00-1 1v1h9V5z"/><path d="M20 5h-8v2h9V6a1 1 0 00-1-1" opacity=".9"/><path d="M12 11V9H3v9a1 1 0 001 1l8-.004V13H5v-2zm-4 4v2H5v-2z"/><path d="M5 15h3v2H5z" opacity=".4"/><path d="M12 9v2h7v2h-7v5.996l8-.004a1 1 0 001-1V9zm3 7h-1v-1h1zm3 0h-1v-1h1z" opacity=".9"/><path d="M14 15h1v1h-1zm3 0h1v1h-1z" opacity=".6"/></svg>';

/** Full link objects reused as GCP sublinks (not listed in `links` on their own). */
export const GCP_CLOUD_RUN_LINK: LinkData = {
    title: 'Cloud Run',
    icon: [CLOUD_RUN_ICON],
    description: 'Google Cloud Run services in the console',
    url: 'https://console.cloud.google.com/run/services',
    chromeProfileEnabled: true,
};

export const GCP_CLOUD_STORAGE_LINK: LinkData = {
    title: 'Cloud Storage',
    icon: [CLOUD_STORAGE_ICON],
    description: 'Google Cloud Storage buckets in the console',
    url: 'https://console.cloud.google.com/storage/browser',
    chromeProfileEnabled: true,
};

export const GCP_BILLING_LINK: LinkData = {
    title: 'Billing',
    icon: [GCP_BILLING_ICON_SVG, GCP_CONSOLE_ICON],
    description: 'Google Cloud billing',
    url: 'https://console.cloud.google.com/billing/01D43D-A00988-01AC64',
    chromeProfileEnabled: true,
};

export const GCP_BILLING_REPORT_BY_PROJECT_LINK: LinkData = {
    title: 'Billing (by project)',
    icon: [GCP_BILLING_ICON_SVG, GCP_CONSOLE_ICON],
    description: 'Billing reports grouped by project',
    url: 'https://console.cloud.google.com/billing/01D43D-A00988-01AC64/reports;chartType=STACKED_BAR;from=2025-04-01;to=2026-04-30;dateType=USAGE_DATE;grouping=GROUP_BY_PROJECT',
    chromeProfileEnabled: true,
};

export const GCP_BILLING_REPORT_BY_SERVICE_LINK: LinkData = {
    title: 'Billing (by service)',
    icon: [GCP_BILLING_ICON_SVG, GCP_CONSOLE_ICON],
    description: 'Billing reports grouped by service',
    url: 'https://console.cloud.google.com/billing/01D43D-A00988-01AC64/reports;timeRange=CUSTOM_RANGE;from=2025-04-01;to=2026-04-30',
    chromeProfileEnabled: true,
};

export const GCP_CONSOLE_LINK: LinkData = {
    title: 'GCP',
    icon: [GCP_CONSOLE_ICON],
    description: 'Google Cloud Platform console',
    url: 'https://console.cloud.google.com/',
    chromeProfileEnabled: true,
    addon: {
        type: 'sublinks',
        items: [
            GCP_CLOUD_RUN_LINK,
            GCP_CLOUD_STORAGE_LINK,
            GCP_BILLING_LINK,
            GCP_BILLING_REPORT_BY_PROJECT_LINK,
            GCP_BILLING_REPORT_BY_SERVICE_LINK,
        ],
    },
};

const LINKEDIN_SVG_BLUE = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%230077b5"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg>';
const LINKEDIN_SVG_WHITE = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="%230077b5"/><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z" fill="white"/></svg>';
export const LINKEDIN_LINK: LinkData = {
    title: 'LinkedIn',
    icon: [
        'https://www.linkedin.com/favicon.ico',
        LINKEDIN_SVG_BLUE,
        LINKEDIN_SVG_WHITE
    ],
    description: 'LinkedIn Feed',
    url: 'https://www.linkedin.com/'
};

const YOUTUBE_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 93 20"><g><path d="M14.4848 20C14.4848 20 23.5695 20 25.8229 19.4C27.0917 19.06 28.0459 18.08 28.3808 16.87C29 14.65 29 9.98 29 9.98C29 9.98 29 5.34 28.3808 3.14C28.0459 1.9 27.0917 0.94 25.8229 0.61C23.5695 0 14.4848 0 14.4848 0C14.4848 0 5.42037 0 3.17711 0.61C1.9286 0.94 0.954148 1.9 0.59888 3.14C0 5.34 0 9.98 0 9.98C0 9.98 0 14.65 0.59888 16.87C0.954148 18.08 1.9286 19.06 3.17711 19.4C5.42037 20 14.4848 20 14.4848 20Z" fill="%23FF0033"/><path d="M19 10L11.5 5.75V14.25L19 10Z" fill="white"/></g><g><path d="M37.1384 18.8999V13.4399L40.6084 2.09994H38.0184L36.6984 7.24994C36.3984 8.42994 36.1284 9.65994 35.9284 10.7999H35.7684C35.6584 9.79994 35.3384 8.48994 35.0184 7.22994L33.7384 2.09994H31.1484L34.5684 13.4399V18.8999H37.1384Z"/><path d="M44.1003 6.29994C41.0703 6.29994 40.0303 8.04994 40.0303 11.8199V13.6099C40.0303 16.9899 40.6803 19.1099 44.0403 19.1099C47.3503 19.1099 48.0603 17.0899 48.0603 13.6099V11.8199C48.0603 8.44994 47.3803 6.29994 44.1003 6.29994ZM45.3903 14.7199C45.3903 16.3599 45.1003 17.3899 44.0503 17.3899C43.0203 17.3899 42.7303 16.3499 42.7303 14.7199V10.6799C42.7303 9.27994 42.9303 8.02994 44.0503 8.02994C45.2303 8.02994 45.3903 9.34994 45.3903 10.6799V14.7199Z"/><path d="M52.2713 19.0899C53.7313 19.0899 54.6413 18.4799 55.3913 17.3799H55.5013L55.6113 18.8999H57.6012V6.53994H54.9613V16.4699C54.6812 16.9599 54.0312 17.3199 53.4212 17.3199C52.6512 17.3199 52.4113 16.7099 52.4113 15.6899V6.53994H49.7812V15.8099C49.7812 17.8199 50.3613 19.0899 52.2713 19.0899Z"/><path d="M62.8261 18.8999V4.14994H65.8661V2.09994H57.1761V4.14994H60.2161V18.8999H62.8261Z"/><path d="M67.8728 19.0899C69.3328 19.0899 70.2428 18.4799 70.9928 17.3799H71.1028L71.2128 18.8999H73.2028V6.53994H70.5628V16.4699C70.2828 16.9599 69.6328 17.3199 69.0228 17.3199C68.2528 17.3199 68.0128 16.7099 68.0128 15.6899V6.53994H65.3828V15.8099C65.3828 17.8199 65.9628 19.0899 67.8728 19.0899Z"/><path d="M80.6744 6.26994C79.3944 6.26994 78.4744 6.82994 77.8644 7.73994H77.7344C77.8144 6.53994 77.8744 5.51994 77.8744 4.70994V1.43994H75.3244L75.3144 12.1799L75.3244 18.8999H77.5444L77.7344 17.6999H77.8044C78.3944 18.5099 79.3044 19.0199 80.5144 19.0199C82.5244 19.0199 83.3844 17.2899 83.3844 13.6099V11.6999C83.3844 8.25994 82.9944 6.26994 80.6744 6.26994ZM80.7644 13.6099C80.7644 15.9099 80.4244 17.2799 79.3544 17.2799C78.8544 17.2799 78.1644 17.0399 77.8544 16.5899V9.23994C78.1244 8.53994 78.7244 8.02994 79.3944 8.02994C80.4744 8.02994 80.7644 9.33994 80.7644 11.7299V13.6099Z"/><path d="M92.6517 11.4999C92.6517 8.51994 92.3517 6.30994 88.9217 6.30994C85.6917 6.30994 84.9717 8.45994 84.9717 11.6199V13.7899C84.9717 16.8699 85.6317 19.1099 88.8417 19.1099C91.3817 19.1099 92.6917 17.8399 92.5417 15.3799L90.2917 15.2599C90.2617 16.7799 89.9117 17.3999 88.9017 17.3999C87.6317 17.3999 87.5717 16.1899 87.5717 14.3899V13.5499H92.6517V11.4999ZM88.8617 7.96994C90.0817 7.96994 90.1717 9.11994 90.1717 11.0699V12.0799H87.5717V11.0699C87.5717 9.13994 87.6517 7.96994 88.8617 7.96994Z"/></g></svg>';
const YOUTUBE_SVG_FALLBACK = '/src/data/youtube-icon-svgrepo-com.svg';
const YOUTUBE_ICON_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -38 256 256"><g><path d="M250.346231,28.0746923 C247.358133,17.0320558 238.732098,8.40602109 227.689461,5.41792308 C207.823743,0 127.868333,0 127.868333,0 C127.868333,0 47.9129229,0.164179487 28.0472049,5.58210256 C17.0045684,8.57020058 8.37853373,17.1962353 5.39043571,28.2388718 C-0.618533519,63.5374615 -2.94988224,117.322662 5.5546152,151.209308 C8.54271322,162.251944 17.1687479,170.877979 28.2113844,173.866077 C48.0771024,179.284 128.032513,179.284 128.032513,179.284 C128.032513,179.284 207.987923,179.284 227.853641,173.866077 C238.896277,170.877979 247.522312,162.251944 250.51041,151.209308 C256.847738,115.861464 258.801474,62.1091 250.346231,28.0746923 Z" fill="%23FF0000"/><polygon fill="%23FFFFFF" points="102.420513 128.06 168.749025 89.642 102.420513 51.224"/></g></svg>';
export const YOUTUBE_LINK: LinkData = {
    title: 'Subscriptions',
    icon: [
        YOUTUBE_SVG_FALLBACK,
        YOUTUBE_ICON_SVG,
        YOUTUBE_SVG
    ],
    description: 'Your YouTube subscription feed',
    url: 'https://www.youtube.com/feed/subscriptions'
};

export const YOUTUBE_STUDIO_LINK: LinkData = {
    title: 'DanielMusicIL\'s Studio',
    icon: [
        YOUTUBE_ICON_SVG,
        YOUTUBE_SVG
    ],
    description: 'YouTube Studio for channel management',
    url: 'https://studio.youtube.com/channel/UCauGG97chgNr-BwoQpKTytg'
};

// Array of all links for easy iteration
export const links: LinkData[] = [
    GITHUB_LINK,
    GMAIL_LINK,
    GOOGLE_CALENDAR_LINK,
    GOOGLE_DRIVE_LINK,
    PYPI_MANAGE_LINK,
    LOCALHOST_BUNDLE_LINK,
    CHATGPT_LINK,
    AWS_CONSOLE_LINK,
    GCP_CONSOLE_LINK,
    LINKEDIN_LINK,
    YOUTUBE_LINK,
    YOUTUBE_STUDIO_LINK,
    GALGALATZ_LINK,
];
