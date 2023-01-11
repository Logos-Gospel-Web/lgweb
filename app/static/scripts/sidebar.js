function registerSidebar(sidebar) {
    var TOP_MARGIN = 72
    var BOTTOM_MARGIN = 64
    var STATE_UNKNOWN = 0
    var STATE_TOP = 1
    var STATE_MIDDLE = 2
    var STATE_BOTTOM = 3

    var container = sidebar.parentElement
    var body = container.parentElement

    var prevTop = container.getBoundingClientRect().top
    var state = STATE_UNKNOWN

    function toParentTop() {
        state = STATE_TOP
        sidebar.style.position = "absolute"
        sidebar.style.top = "0"
        sidebar.style.bottom = "auto"
    }

    function toMarginTop() {
        state = STATE_TOP
        sidebar.style.position = "fixed"
        sidebar.style.top = TOP_MARGIN + "px"
        sidebar.style.bottom = "auto"
    }

    function toParentBottom() {
        state = STATE_BOTTOM
        sidebar.style.position = "absolute"
        sidebar.style.top = "auto"
        sidebar.style.bottom = "0"
    }

    function toMarginBottom() {
        state = STATE_BOTTOM
        sidebar.style.position = "fixed"
        sidebar.style.top = "auto"
        sidebar.style.bottom = BOTTOM_MARGIN + "px"
    }

    function toAbsolute(top) {
        state = STATE_MIDDLE
        sidebar.style.position = "absolute"
        sidebar.style.top = top.toFixed(2) + "px"
        sidebar.style.bottom = "auto"
    }

    function onScroll() {
        var parentRect = container.getBoundingClientRect()
        if (parentRect.height === 0) return

        var maxTop = TOP_MARGIN

        if (parentRect.top > maxTop) {
            toParentTop()
        } else {
            var winHeight = window.innerHeight
            var maxBottom = winHeight - BOTTOM_MARGIN
            var rect = sidebar.getBoundingClientRect()

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

    var unlisten = listen(window, "scroll", onScroll, true)

    var close = sidebar.querySelector(".sidebar__close")
    function onClose() {
        body.classList.add("sidebar-container--closed")
        unlisten()
    }
    if (close) {
        close.addEventListener("click", onClose)
    }
    onScroll()

    return function() {
        if (close) {
            close.removeEventListener("click", onClose)
        }
        unlisten()
    }
}

var sidebar = document.querySelector(".sidebar__content")

if (sidebar) {
    registerSidebar(sidebar)
}
