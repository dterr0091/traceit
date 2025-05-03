declare module '@sparticuz/chromium' {
  const args: string[];
  const headless: boolean | 'new';
  function executablePath(executablePath?: string): Promise<string>;
  export default {
    args,
    headless,
    executablePath
  };
} 