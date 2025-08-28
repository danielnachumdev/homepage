# Customizable Homepage

A fully customizable personal homepage built with modern web technologies, featuring a Python FastAPI backend, React TypeScript frontend, and an optional Chrome browser extension for profile detection and enhanced customization.

## 🎯 Project Aim

This project aims to create a personalized, feature-rich homepage that adapts to your needs and preferences. Whether you're a developer, designer, or power user, this homepage provides a centralized hub for your daily digital activities with the following key features:

- **Personalized Dashboard**: Customizable widgets, layouts, and themes
- **Profile-Aware Customization**: Browser extension integration for Chrome profile detection
- **Responsive Design**: Works seamlessly across all devices and screen sizes
- **Fast Performance**: Built with Vite and optimized for speed
- **Extensible Architecture**: Easy to add new features and integrations

## 🏗️ Architecture Overview

The project consists of three main components that work together to create a seamless user experience:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Browser       │
│   (React + TS)  │◄──►│  (FastAPI)      │◄──►│   Extension     │
│   + Vite        │    │   + Python      │    │   (Chrome)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### 🎨 Frontend (`/frontend`)
- **Technology Stack**: React 18 + TypeScript + Vite
- **Styling**: Modern CSS with responsive design principles
- **State Management**: React hooks and context API
- **Build Tool**: Vite for fast development and optimized builds
- **Features**:
  - Customizable widget system
  - Drag-and-drop layout management
  - Theme switching (light/dark mode)
  - Responsive grid layouts
  - Local storage for user preferences

#### 🐍 Backend (`/backend`)
- **Technology Stack**: Python 3.11+ + FastAPI + SQLAlchemy
- **API Design**: RESTful API with OpenAPI documentation
- **Database**: SQLite for development, PostgreSQL for production
- **Features**:
  - User authentication and profile management
  - Widget configuration storage
  - Theme and layout persistence
  - API endpoints for customization
  - Real-time updates via WebSockets

#### 🔌 Browser Extension (`/browser-extension`)
- **Technology Stack**: Vanilla JavaScript + Chrome Extension API
- **Purpose**: Chrome profile detection and enhanced customization
- **Features**:
  - Active Chrome profile detection
  - Profile-specific homepage configurations
  - Seamless integration with main application
  - Optional installation (not required for core functionality)

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- Chrome browser (for extension features)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd homepage
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

#### Backend Development
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Browser Extension Development
```bash
cd browser-extension
# Load the extension in Chrome:
# 1. Open Chrome and go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked" and select the browser-extension folder
```

## 📁 Project Structure

```
homepage/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React TypeScript frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── browser-extension/      # Chrome extension
│   ├── manifest.json
│   ├── background.js
│   └── content.js
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./homepage.db

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=My Custom Homepage

# Docker Configuration
COMPOSE_PROJECT_NAME=homepage
```

### Customization Options
- **Widgets**: Add, remove, and configure dashboard widgets
- **Layouts**: Customize grid layouts and positioning
- **Themes**: Choose from predefined themes or create custom ones
- **Profiles**: Set up different configurations for different Chrome profiles

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app
```

## 📦 Deployment

### Production Build
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configurations
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `docker-compose.test.yml` - Testing environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join the conversation in GitHub Discussions
- **Documentation**: Check the `/docs` folder for detailed guides

## 🔮 Roadmap

- [ ] Widget marketplace for community-created widgets
- [ ] Advanced theming system with CSS custom properties
- [ ] Mobile app companion
- [ ] Integration with popular productivity tools
- [ ] Multi-language support
- [ ] Advanced analytics and usage insights

---

**Built with ❤️ using modern web technologies**
