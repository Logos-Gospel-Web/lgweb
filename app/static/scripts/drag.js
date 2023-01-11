function getPoint(ev) {
    return { x: ev.clientX, y: ev.clientY }
}

function createDrag(options) {
    var elem = options.elem
    var preventDefault = options.preventDefault

    var unregisterMouse = { f: noop }
    var mousedown = listen(elem, "mousedown", function(ev) {
        if (preventDefault) ev.preventDefault()
        function onMouseMove(ev) {
            if (preventDefault) ev.preventDefault()
            options.onMove(getPoint(ev))
        }
        function onMouseUp(ev) {
            if (preventDefault) ev.preventDefault()
            options.onEnd()
            unregisterMouse.f()
            unregisterMouse.f = noop
        }
        var mousemove = listen(document, "mousemove", onMouseMove, !preventDefault)
        var mouseup = listen(document, "mouseup", onMouseUp, !preventDefault)
        unregisterMouse.f = function() {
            mousemove()
            mouseup()
        }
        options.onStart(getPoint(ev))
    }, !preventDefault)

    var touches = 0
    var unregisterTouch = { f: noop }
    var touchstart = listen(elem, "touchstart", function(ev) {
        if (preventDefault) ev.preventDefault()
        var p = getPoint(ev.touches[0])
        if (touches) {
            options.onMove(p)
        } else {
            function onTouchChange(ev) {
                if (preventDefault) ev.preventDefault()
                touches = ev.touches.length
                if (touches) {
                    options.onMove(getPoint(ev.touches[0]))
                } else {
                    options.onEnd()
                    unregisterTouch.f()
                    unregisterTouch.f = noop
                }
            }
            var touchmove = listen(document, "touchmove", onTouchChange, !preventDefault)
            var touchend = listen(document, "touchend", onTouchChange, !preventDefault)
            var touchcancel = listen(document, "touchcancel", onTouchChange, !preventDefault)
            unregisterTouch.f = function() {
                touchmove()
                touchend()
                touchcancel()
            }
            options.onStart(p)
        }
        touches = ev.touches.length
    }, !preventDefault)

    return function() {
        touchstart()
        mousedown()
        unregisterTouch.f()
        unregisterMouse.f()
    }
}
