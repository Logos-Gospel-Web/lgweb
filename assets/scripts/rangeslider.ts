import { createDrag } from './drag'

export type RangeSliderOptions = {
    value?: number
    min?: number
    max?: number
    onChange?: (val: number) => void
    onActive?: (val: number) => void
    onInactive?: (val: number) => void
}

export type RangeSlider = {
    element: HTMLElement
    val: (v?: number) => number
}

export function createRangeSlider(options: RangeSliderOptions): RangeSlider {
    const min = options.min || 0
    const max = options.max || 0
    const onChange = options.onChange
    const onActive = options.onActive
    const onInactive = options.onInactive
    const len = max - min

    let value: number | null = null

    const thumb = document.createElement('div')
    thumb.className = 'slider__thumb'

    const range = document.createElement('div')
    range.className = 'slider__range'
    range.appendChild(thumb)

    const slider = document.createElement('div')
    slider.className = 'slider'
    slider.appendChild(range)

    let pending: number | null = null

    function sync() {
        range.style.maxWidth = (((value! - min) * 100) / len).toFixed(2) + '%'
        if (onChange) onChange(value!)
    }

    function setValue(val: number) {
        const v = val < min ? min : val > max ? max : val
        if (v === value) return
        if (pending === null) {
            value = v
            setTimeout(() => {
                if (pending !== null && value !== pending) {
                    value = pending
                    sync()
                }
                pending = null
            }, 50)
            sync()
        }
        pending = v
    }

    function setValueByPosition(pos: number) {
        const rect = slider.getBoundingClientRect()
        setValue(((pos - rect.left) * len) / rect.width + min)
    }

    createDrag({
        elem: slider,
        onStart(p) {
            if (onActive) onActive(value!)
            setValueByPosition(p.x)
        },
        onMove(p) {
            setValueByPosition(p.x)
        },
        onEnd() {
            if (onInactive) onInactive(value!)
        },
    })

    setValue(options.value || min)

    return {
        element: slider,
        val(v?: number) {
            if (v !== undefined) {
                setValue(v)
            }
            return value!
        },
    }
}
