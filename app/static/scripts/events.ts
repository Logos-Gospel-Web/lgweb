import { supportPassiveListener } from '@/constants'

export function listen<K extends keyof DocumentEventMap>(
    elem: Document,
    event: K,
    listener: (ev: DocumentEventMap[K]) => void,
    passive?: boolean,
): () => void
export function listen<K extends keyof WindowEventMap>(
    elem: Window,
    event: K,
    listener: (ev: WindowEventMap[K]) => void,
    passive?: boolean,
): () => void
export function listen<K extends keyof HTMLElementEventMap>(
    elem: HTMLElement,
    event: K,
    listener: (ev: HTMLElementEventMap[K]) => void,
    passive?: boolean,
): () => void
export function listen(
    elem: any,
    event: string,
    listener: (ev: any) => void,
    passive?: boolean,
) {
    const options =
        supportPassiveListener && passive !== undefined ? { passive } : false
    elem.addEventListener(event, listener, options)
    return function () {
        elem.removeEventListener(event, listener, false)
    }
}

// Stop propagation does not work here
export function delegate<K extends keyof HTMLElementEventMap>(
    selector: string,
    event: K,
    listener: (ev: HTMLElementEventMap[K]) => void,
    passive?: boolean,
) {
    const fn = function (evt: Event) {
        let el = evt.target as HTMLElement | null

        if (el) {
            el = el.closest(selector)
            if (el) {
                const newEvt = Object.create(evt)
                Object.defineProperties(newEvt, {
                    target: { value: evt.target },
                    currentTarget: { value: el },
                    preventDefault: {
                        value: function () {
                            evt.preventDefault()
                        },
                    },
                })
                listener(newEvt)
            }
        }
    }
    return listen(document.body, event, fn, passive)
}
