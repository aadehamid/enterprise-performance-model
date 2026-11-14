/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly PACKAGE_VERSION: string;
  readonly VITE_BACKEND_URL?: string;
  readonly VITE_HELP_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
