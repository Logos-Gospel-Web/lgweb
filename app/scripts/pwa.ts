function registerServiceWorker() {
    const script = document.currentScript
    if (!script) return
    const src = script.getAttribute('src')
    if (!src) return
    const index = src.indexOf('?')
    if (index === -1) return
    navigator.serviceWorker.register(
        '/static/compiled/sw.js' + src.slice(index),
    )
}

if ('serviceWorker' in navigator) {
    registerServiceWorker()
}
