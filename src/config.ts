export const USE_DEMO = (import.meta.env.VITE_USE_DEMO ?? 'false') === 'true'
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || ''
