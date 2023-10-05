import { noop } from './common'
import { listen } from './events'

type Point = {
    x: number
    y: number
}

type DragOptions = {
    elem: HTMLElement
    onStart: (point: Point, preventDefault: () => void) => void
    onMove: (point: Point, preventDefault: () => void) => void
    onEnd: (preventDefault: () => void) => void
}

function getPoint(ev: any): Point {
    return { x: ev.clientX, y: ev.clientY }
}

export function createDrag(options: DragOptions): () => void {
    const elem = options.elem

    let unregisterMouse = noop
    const mousedown = listen(elem, 'mousedown', function (ev) {
        function onMouseMove(ev: MouseEvent) {
            options.onMove(getPoint(ev), function () {
                ev.preventDefault()
            })
        }
        function onMouseUp(ev: MouseEvent) {
            options.onEnd(function () {
                ev.preventDefault()
            })
            unregisterMouse()
            unregisterMouse = noop
        }
        const mousemove = listen(document, 'mousemove', onMouseMove)
        const mouseup = listen(document, 'mouseup', onMouseUp)
        unregisterMouse = function () {
            mousemove()
            mouseup()
        }
        options.onStart(getPoint(ev), function () {
            ev.preventDefault()
        })
    })

    let touches = 0
    let unregisterTouch = noop
    const touchstart = listen(elem, 'touchstart', function (ev) {
        function onTouchChange(ev: TouchEvent) {
            touches = ev.touches.length
            if (touches) {
                options.onMove(getPoint(ev.touches[0]), function () {
                    ev.preventDefault()
                })
            } else {
                options.onEnd(function () {
                    ev.preventDefault()
                })
                unregisterTouch()
                unregisterTouch = noop
            }
        }
        const p = getPoint(ev.touches[0])
        if (touches) {
            options.onMove(p, function () {
                ev.preventDefault()
            })
        } else {
            const touchmove = listen(document, 'touchmove', onTouchChange)
            const touchend = listen(document, 'touchend', onTouchChange)
            const touchcancel = listen(document, 'touchcancel', onTouchChange)
            unregisterTouch = function () {
                touchmove()
                touchend()
                touchcancel()
            }
            options.onStart(p, function () {
                ev.preventDefault()
            })
        }
        touches = ev.touches.length
    })

    return function () {
        touchstart()
        mousedown()
        unregisterTouch()
        unregisterMouse()
    }
}
