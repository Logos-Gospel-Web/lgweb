import { noop } from './common'
import { listen } from './events'

type Point = {
    x: number
    y: number
}

type DragOptions = {
    elem: HTMLElement
    onStart: (point: Point) => void
    onMove: (point: Point) => void
    onEnd: (preventDefault: () => void) => void
}

function getPoint(ev: any): Point {
    return { x: ev.clientX, y: ev.clientY }
}

export function createDrag(options: DragOptions): () => void {
    const elem = options.elem

    let unregisterMouse = noop
    const mousedown = listen(elem, 'mousedown', (ev) => {
        function onMouseMove(ev: MouseEvent) {
            options.onMove(getPoint(ev))
        }
        function onMouseUp(ev: MouseEvent) {
            options.onEnd(() => {
                ev.preventDefault()
            })
            unregisterMouse()
            unregisterMouse = noop
        }
        const mousemove = listen(document, 'mousemove', onMouseMove)
        const mouseup = listen(document, 'mouseup', onMouseUp)
        unregisterMouse = () => {
            mousemove()
            mouseup()
        }
        options.onStart(getPoint(ev))
    })

    let touches = 0
    let unregisterTouch = noop
    const touchstart = listen(elem, 'touchstart', (ev) => {
        function onTouchChange(ev: TouchEvent) {
            touches = ev.touches.length
            if (touches) {
                options.onMove(getPoint(ev.touches[0]))
            } else {
                options.onEnd(() => {
                    ev.preventDefault()
                })
                unregisterTouch()
                unregisterTouch = noop
            }
        }
        const p = getPoint(ev.touches[0])
        if (touches) {
            options.onMove(p)
        } else {
            const touchmove = listen(document, 'touchmove', onTouchChange)
            const touchend = listen(document, 'touchend', onTouchChange)
            const touchcancel = listen(document, 'touchcancel', onTouchChange)
            unregisterTouch = () => {
                touchmove()
                touchend()
                touchcancel()
            }
            options.onStart(p)
        }
        touches = ev.touches.length
    })

    return () => {
        touchstart()
        mousedown()
        unregisterTouch()
        unregisterMouse()
    }
}
