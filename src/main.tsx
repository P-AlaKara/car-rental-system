import * as React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AppProd from './App.tsx'
import AppDemo from './App_NEW.tsx'
import { USE_DEMO } from './config'
import Toaster from './components/Toaster'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {USE_DEMO ? <AppDemo /> : <AppProd />}
    <Toaster />
  </React.StrictMode>,
)
