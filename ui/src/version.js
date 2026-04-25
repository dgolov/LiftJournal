// Injected at build time from package.json by vite.config.js.
// To release a new version:
//   npm version patch   → 1.0.0 → 1.0.1  (bug fixes)
//   npm version minor   → 1.0.0 → 1.1.0  (new features)
//   npm version major   → 1.0.0 → 2.0.0  (breaking changes)
// Then add an entry to src/changelog.js.

/* global __APP_VERSION__, __BUILD_DATE__ */
export const APP_VERSION = __APP_VERSION__
export const BUILD_DATE = __BUILD_DATE__
