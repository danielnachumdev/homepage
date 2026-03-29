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

#### 🔌 Browser Extension (`/extension`)
- **Technology Stack**: TypeScript + Chrome Extension API (see `extension/package.json`)
- **Purpose**: Chrome profile detection and enhanced customization
- **Features**:
  - Active Chrome profile detection
  - Profile-specific homepage configurations
  - Seamless integration with main application
  - Optional installation (not required for core functionality)

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python venv and dependency installs)
- Node.js 18 or higher
- Docker and Docker Compose (optional; for containerized run)
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

From the repository root, install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
npm install
npm run install
```

That runs backend install (`uv sync` from the repo root), frontend `npm i`, and extension installs in parallel (see root `package.json`).

#### Full stack (backend + frontend)
```bash
npm run dev
```

#### Frontend only
```bash
cd frontend
npm install
npm run dev
```

#### Backend only
```bash
uv sync
cd backend && uv run python __main__.py
```

#### Browser extension
Load unpacked from the `extension/` folder in Chrome (`chrome://extensions/` → Developer mode → Load unpacked). Build steps, if any, are in `extension/package.json` and `extension/popup/package.json`.

## 📁 Project Structure

```
homepage/
├── package.json            # Root scripts: install, dev, test (uses uv for backend)
├── pyproject.toml          # Python deps (uv); uv.lock for lockfile
├── backend/                # Python FastAPI backend
│   ├── __main__.py
│   ├── src/
│   └── Dockerfile
├── frontend/               # React TypeScript frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── extension/              # Chrome extension
│   ├── manifest.json
│   ├── package.json
│   └── popup/
├── docker-compose.yml      # Multi-service orchestration
└── README.md               # This file
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

From the repository root:

```bash
npm run test
```

That runs backend tests (`uv run pytest` from the repo root; see `pyproject.toml`), frontend tests, and extension tests (see root `package.json`).

### Frontend only
```bash
cd frontend
npm run test
```

### Backend only
```bash
uv run pytest
```
Run from the repository root so `pyproject.toml` pytest settings apply.

## 📦 Deployment

Docker-based deployment uses `docker-compose.yml` in this repository. Adjust compose files and env for your hosting environment; see `deploy.py` and `deployment/` if you use the project deployment tooling.

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
