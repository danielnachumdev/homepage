# Internet Speed Test Widget

This implementation provides a real-time internet speed test widget that displays download/upload speeds and ping latency in the homepage header.

## Features

- **Real-time Speed Testing**: Continuously tests internet speed at configurable intervals
- **Smart Formatting**: Automatically formats speeds in appropriate units (KB/s, MB/s, GB/s)
- **Auto-start**: Automatically begins testing when the widget loads
- **Visual Status Indicators**: Shows different colors and icons based on status
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Graceful error handling with user-friendly messages

## Backend Implementation

### Dependencies
- `speedtest-cli`: Python library for internet speed testing

### API Endpoints

- `POST /api/v1/speedtest/test` - Perform a single speed test
- `POST /api/v1/speedtest/start` - Start continuous speed testing
- `POST /api/v1/speedtest/stop` - Stop continuous speed testing
- `GET /api/v1/speedtest/status` - Get current testing status
- `GET /api/v1/speedtest/result` - Get latest test result
- `GET /api/v1/speedtest/config` - Get current configuration

### Service Architecture

The `SpeedTestService` handles:
- Single speed test execution
- Continuous testing with configurable intervals
- Result formatting and storage
- Error handling and logging

## Frontend Implementation

### Component Structure

The `SpeedTestWidget` component:
- Uses the API Request Manager for all HTTP requests
- Implements auto-start functionality
- Provides detailed loading states with descriptive messages
- Formats speed values intelligently
- Handles continuous polling for real-time updates

### Display Format

The widget displays:
- **Top Row**: Download speed / Upload speed
- **Bottom Row**: Ping latency (smaller font)
- **Status Icons**: 
  - 🌐 Ready to start
  - ⏳ Testing in progress
  - 🔄 Continuous testing active
  - ❌ Error state

### Speed Formatting Logic

- **≥ 1000 Mbps**: Display as GB/s (e.g., "1.5 GB/s")
- **≥ 1 Mbps**: Display as MB/s (e.g., "45.2 MB/s")  
- **< 1 Mbps**: Display as KB/s (e.g., "750 KB/s")

## Usage

### Basic Usage

```tsx
import { SpeedTestWidget } from './components/Header';

// Auto-start with 1-second interval
<SpeedTestWidget intervalSeconds={1} autoStart={true} />

// Manual start with 5-second interval
<SpeedTestWidget intervalSeconds={5} autoStart={false} />
```

### Props

- `intervalSeconds?: number` - Interval between tests (default: 1)
- `autoStart?: boolean` - Auto-start testing on mount (default: true)
- `className?: string` - Additional CSS classes

## Installation

### Backend Dependencies

```bash
cd backend
pip install speedtest-cli
```

### Frontend Dependencies

No additional dependencies required - uses existing API Request Manager.

## Configuration

The speed test interval can be configured via the `intervalSeconds` prop. The backend supports intervals from 1 to 300 seconds.

## Error Handling

The widget handles various error scenarios:
- Network connectivity issues
- Backend service unavailable
- Speed test failures
- Invalid responses

All errors are displayed with user-friendly messages and appropriate visual indicators.

## Performance Considerations

- Continuous testing is limited to reasonable intervals (1-300 seconds)
- Results are cached to avoid unnecessary API calls
- Automatic cleanup of intervals and tasks on component unmount
- Efficient polling only when continuous testing is active

## Testing

To test the backend functionality:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run the backend
python -m src

# Test the API endpoints
curl -X POST http://localhost:8000/api/v1/speedtest/test
curl -X GET http://localhost:8000/api/v1/speedtest/status
```

## Troubleshooting

### Common Issues

1. **"Speed test failed" errors**: Check internet connectivity and backend service status
2. **No results displayed**: Verify backend is running and accessible
3. **Continuous testing not starting**: Check browser console for API errors
4. **Slow performance**: Consider increasing the test interval

### Debug Mode

Enable debug logging by checking the browser console for detailed error messages and API request/response information.
