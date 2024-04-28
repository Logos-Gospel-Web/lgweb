function registerServiceWorker() {
    const pwaVersion = '?v1'
    navigator.serviceWorker.register('/sw.js' + pwaVersion)
}

if ('serviceWorker' in navigator) {
    registerServiceWorker()
}
