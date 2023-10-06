import { noop } from './common'

export const supportPassiveListener = (() => {
    let supportsPassiveOption = false
    try {
        const opts = Object.defineProperty({}, 'passive', {
            get() {
                supportsPassiveOption = true
            },
        })
        const fn = noop
        window.addEventListener('test', fn, opts)
        window.removeEventListener('test', fn, opts)
    } catch (e) {
        // ignored
    }
    return supportsPassiveOption
})()

export const supportServiceWorker = 'serviceWorker' in navigator

export const supportHistory = !!(window.history && window.history.pushState)
