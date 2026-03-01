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

export function createDrag(options: DragOptions) {
    const elem = options.elem

    let isMouseDown = false
    listen(elem, 'mousedown', (ev) => {
        isMouseDown = true
        options.onStart(getPoint(ev))
    })
    listen(document, 'mousemove', (ev) => {
        if (isMouseDown) {
            options.onMove(getPoint(ev))
        }
    })
    listen(document, 'mouseup', (ev) => {
        if (isMouseDown) {
            options.onEnd(() => {
                ev.preventDefault()
            })
            isMouseDown = false
        }
    })

    let touches = 0
    let isTouchDown = false
    function onTouchChange(ev: TouchEvent) {
        if (isTouchDown) {
            touches = ev.touches.length
            if (touches) {
                options.onMove(getPoint(ev.touches[0]))
            } else {
                options.onEnd(() => {
                    ev.preventDefault()
                })
                isTouchDown = false
            }
        }
    }
    listen(elem, 'touchstart', (ev) => {
        const p = getPoint(ev.touches[0])
        if (touches) {
            options.onMove(p)
        } else {
            options.onStart(p)
        }
        touches = ev.touches.length
    })
    listen(document, 'touchmove', onTouchChange)
    listen(document, 'touchend', onTouchChange)
    listen(document, 'touchcancel', onTouchChange)
}
