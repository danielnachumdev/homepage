import { useBackendStatus } from '../hooks/useBackendStatus'
import './BackendStatus.css'

interface BackendStatusProps {
    checkInterval?: number;
}

export const BackendStatus = ({ checkInterval = 5000 }: BackendStatusProps) => {
    const backendStatus = useBackendStatus(checkInterval);

    return (
        <div className="backend-status">
            <div className="status-indicator">
                <div className={`status-dot ${backendStatus.isConnected ? 'connected' : 'disconnected'}`}></div>
                <span className="status-text">
                    {backendStatus.isConnected ? 'Backend Connected' : 'Backend Disconnected'}
                </span>
            </div>

            {backendStatus.lastChecked && (
                <div className="last-checked">
                    Last checked: {backendStatus.lastChecked.toLocaleTimeString()}
                </div>
            )}

            {backendStatus.error && (
                <div className="error-message">
                    Error: {backendStatus.error}
                </div>
            )}
        </div>
    );
};
