import { createContext, useMemo, useState, useEffect, ReactNode } from 'react';
import { NeedleThemeProvider } from '@neo4j-ndl/react';

type ColorMode = 'light' | 'dark';

export const ThemeWrapperContext = createContext({
  toggleColorMode: () => {},
  colorMode: 'dark' as ColorMode,
});

interface ThemeWrapperProps {
  children: ReactNode;
}

export default function ThemeWrapper({ children }: ThemeWrapperProps) {
  const [mode, setMode] = useState<ColorMode>('dark');

  const themeWrapperUtils = useMemo(
    () => ({
      colorMode: mode,
      toggleColorMode: () => setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light')),
    }),
    [mode]
  );

  useEffect(() => {
    document.body.classList.toggle('ndl-theme-dark', mode === 'dark');
    document.documentElement.style.colorScheme = mode;
  }, [mode]);

  return (
    <ThemeWrapperContext value={themeWrapperUtils}>
      <NeedleThemeProvider theme={mode} wrapperProps={{ isWrappingChildren: true }}>
        {children}
      </NeedleThemeProvider>
    </ThemeWrapperContext>
  );
}
