import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
//import './index.css' // We are using Tailwind, but keeping this import if user adds global css later.

// Since we are using Tailwind via CDN in index.html, we don't strictly need a CSS file for tailwind directives
// unless we set up PostCSS. For this "runnable" request, CDN is safer

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
