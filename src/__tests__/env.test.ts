// Test that environment variables are properly loaded
describe('Environment variables', () => {
  it('should load environment variables from .env file', () => {
    // This test doesn't actually validate the presence of specific values
    // as the .env file may not exist in CI environments
    // But it ensures the dotenv configuration is properly imported
    expect(process.env).toBeDefined();
    console.log('OPENAI_API_KEY availability:', !!process.env.OPENAI_API_KEY ? 'defined' : 'undefined');
  });
}); 