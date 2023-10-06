export const supportPassiveListener = (function () {
    let supportsPassiveOption = false
    try {
        const opts = Object.defineProperty({}, 'passive', {
            get: function () {
                supportsPassiveOption = true
            },
        })
        const fn = function () {}
        window.addEventListener('test', fn, opts)
        window.removeEventListener('test', fn, opts)
    } catch (e) {
        // ignored
    }
    return supportsPassiveOption
})()

export const supportServiceWorker = 'serviceWorker' in navigator

export const supportHistory = !!(window.history && window.history.pushState)
