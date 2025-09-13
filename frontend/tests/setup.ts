import '@testing-library/jest-dom'
import { afterAll } from 'vitest'
import { initFetchMock, cleanupFetchMock } from './utils/fetch-mock'

// Initialize fetch mocking for all tests
initFetchMock()

// Clean up after all tests
afterAll(() => {
    cleanupFetchMock()
})
