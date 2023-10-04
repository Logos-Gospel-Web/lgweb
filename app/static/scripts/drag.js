function getPoint(ev) {
    return { x: ev.clientX, y: ev.clientY }
}

function createDrag(options) {
    var elem = options.elem

    var unregisterMouse = noop
    var mousedown = listen(elem, "mousedown", function(ev) {
        function onMouseMove(ev) {
            options.onMove(getPoint(ev), function () { ev.preventDefault() })
        }
        function onMouseUp(ev) {
            options.onEnd(function () { ev.preventDefault() })
            unregisterMouse()
            unregisterMouse = noop
        }
        var mousemove = listen(document, "mousemove", onMouseMove)
        var mouseup = listen(document, "mouseup", onMouseUp)
        unregisterMouse = function() {
            mousemove()
            mouseup()
        }
        options.onStart(getPoint(ev), function () { ev.preventDefault() })
    })

    var touches = 0
    var unregisterTouch = noop
    var touchstart = listen(elem, "touchstart", function(ev) {
        var p = getPoint(ev.touches[0])
        if (touches) {
            options.onMove(p, function () { ev.preventDefault() })
        } else {
            function onTouchChange(ev) {
                touches = ev.touches.length
                if (touches) {
                    options.onMove(getPoint(ev.touches[0], function () { ev.preventDefault() }))
                } else {
                    options.onEnd(function () { ev.preventDefault() })
                    unregisterTouch()
                    unregisterTouch = noop
                }
            }
            var touchmove = listen(document, "touchmove", onTouchChange)
            var touchend = listen(document, "touchend", onTouchChange)
            var touchcancel = listen(document, "touchcancel", onTouchChange)
            unregisterTouch = function() {
                touchmove()
                touchend()
                touchcancel()
            }
            options.onStart(p, function () { ev.preventDefault() })
        }
        touches = ev.touches.length
    })

    return function() {
        touchstart()
        mousedown()
        unregisterTouch()
        unregisterMouse()
    }
}
