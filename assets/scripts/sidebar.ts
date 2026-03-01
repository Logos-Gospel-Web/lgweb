import { listen } from './events'

function registerSidebar(sidebar: HTMLElement) {
    const TOP_MARGIN = 72
    const BOTTOM_MARGIN = 64
    const STATE_UNKNOWN = 0
    const STATE_TOP = 1
    const STATE_MIDDLE = 2
    const STATE_BOTTOM = 3

    const container = sidebar.parentElement!
    const body = container.parentElement!

    let prevTop = container.getBoundingClientRect().top
    let state = STATE_UNKNOWN

    function toParentTop() {
        state = STATE_TOP
        sidebar.style.position = 'absolute'
        sidebar.style.top = '0'
        sidebar.style.bottom = 'auto'
    }

    function toMarginTop() {
        state = STATE_TOP
        sidebar.style.position = 'fixed'
        sidebar.style.top = TOP_MARGIN + 'px'
        sidebar.style.bottom = 'auto'
    }

    function toParentBottom() {
        state = STATE_BOTTOM
        sidebar.style.position = 'absolute'
        sidebar.style.top = 'auto'
        sidebar.style.bottom = '0'
    }

    function toMarginBottom() {
        state = STATE_BOTTOM
        sidebar.style.position = 'fixed'
        sidebar.style.top = 'auto'
        sidebar.style.bottom = BOTTOM_MARGIN + 'px'
    }

    function toAbsolute(top: number) {
        state = STATE_MIDDLE
        sidebar.style.position = 'absolute'
        sidebar.style.top = top.toFixed(2) + 'px'
        sidebar.style.bottom = 'auto'
    }

    function onScroll() {
        const parentRect = container.getBoundingClientRect()
        if (parentRect.height === 0) return

        const maxTop = TOP_MARGIN

        if (parentRect.top > maxTop) {
            toParentTop()
        } else {
            const winHeight = window.innerHeight
            const maxBottom = winHeight - BOTTOM_MARGIN
            const rect = sidebar.getBoundingClientRect()

            if (rect.bottom - parentRect.bottom >= -0.1) {
                if (rect.top > maxTop) {
                    toMarginTop()
                } else {
                    toParentBottom()
                }
            } else if (maxBottom - maxTop >= rect.height) {
                // Sidebar height is smaller than window height
                toMarginTop()
            } else if (parentRect.top < prevTop) {
                // Scrolling down
                if (state === STATE_TOP) {
                    toAbsolute(rect.top - parentRect.top)
                } else if (state !== STATE_BOTTOM && rect.bottom < maxBottom) {
                    toMarginBottom()
                }
            } else {
                // Scrolling up
                if (state === STATE_BOTTOM) {
                    toAbsolute(rect.top - parentRect.top)
                } else if (state !== STATE_TOP && rect.top > maxTop) {
                    toMarginTop()
                }
            }
        }
        prevTop = parentRect.top
    }

    listen(window, 'scroll', onScroll, true)

    const close = sidebar.querySelector<HTMLElement>('.sidebar__close')
    function onClose() {
        body.classList.add('sidebar-container--closed')
        window.removeEventListener('scroll', onScroll)
    }
    if (close) {
        listen(close, 'click', onClose)
    }
    onScroll()
}

const sidebar = document.querySelector<HTMLElement>('.sidebar__content')

if (sidebar) {
    registerSidebar(sidebar)
}
