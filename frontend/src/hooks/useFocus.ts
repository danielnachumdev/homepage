import { useCallback } from 'react';

/**
 * Custom hook that provides a focus function for any HTML element
 * @returns A function that takes an HTMLElement and focuses it
 */
export const useFocus = () => {
    const focus = useCallback((element: HTMLElement | null) => {
        if (element) {
            // If it's not an input element, try to find the actual input inside
            let inputElement = element;
            if (!(element instanceof HTMLInputElement)) {
                const input = element.querySelector('input');
                if (input) {
                    inputElement = input;
                } else {
                    return;
                }
            }

            // Now focus the actual input element
            if (inputElement.focus) {
                inputElement.focus();

                // Select the text if any
                if (inputElement instanceof HTMLInputElement) {
                    inputElement.select();
                }
            }
        }
    }, []);

    return focus;
};
