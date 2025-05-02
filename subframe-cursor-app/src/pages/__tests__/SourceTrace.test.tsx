import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SourceTrace from '../SourceTrace';

describe('SourceTrace', () => {
  it('should call handleSearch when trace button is clicked', () => {
    // Mock console.log to verify the search is triggered
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    render(<SourceTrace />);
    
    // Find and click the trace button
    const traceButton = screen.getByText('Trace');
    fireEvent.click(traceButton);
    
    // Verify that handleSearch was called
    expect(consoleSpy).toHaveBeenCalledWith('Searching for:', '');
    
    // Clean up
    consoleSpy.mockRestore();
  });

  it('should pass search query and images to handleSearch', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    render(<SourceTrace />);
    
    // Enter a search query
    const searchInput = screen.getByPlaceholderText(/Search for content to trace/);
    fireEvent.change(searchInput, { target: { value: 'test query' } });
    
    // Click the trace button
    const traceButton = screen.getByText('Trace');
    fireEvent.click(traceButton);
    
    // Verify that handleSearch was called with the correct query
    expect(consoleSpy).toHaveBeenCalledWith('Searching for:', 'test query');
    
    // Clean up
    consoleSpy.mockRestore();
  });
}); 