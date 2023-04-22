
function createRangeSlider(options) {
    var min = options.min || 0
    var max = options.max || 0
    var onChange = options.onChange
    var onActive = options.onActive
    var onInactive = options.onInactive
    var len = max - min

    var value = null

    var thumb = document.createElement("div")
    thumb.className = "slider__thumb"

    var range = document.createElement("div")
    range.className = "slider__range"
    range.appendChild(thumb)

    var slider = document.createElement("div")
    slider.className = "slider"
    slider.appendChild(range)

    var pending = null

    function sync() {
        range.style.maxWidth = (((value - min) * 100) / len).toFixed(2) + "%"
        if (onChange) onChange(value)
    }

    function setValue(val) {
        var v = val < min ? min : val > max ? max : val
        if (v === value) return
        if (pending === null) {
            value = v
            setTimeout(function() {
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

    function setValueByPosition(pos) {
        var rect = slider.getBoundingClientRect()
        setValue(((pos - rect.left) * len) / rect.width + min)
    }

    var unregister = createDrag({
        elem: slider,
        onStart: function(p) {
            if (onActive) onActive(value)
            setValueByPosition(p.x)
        },
        onMove: function(p) {
            setValueByPosition(p.x)
        },
        onEnd: function() {
            if (onInactive) onInactive(value)
        },
    })

    setValue(options.value || min)

    return {
        element: slider,
        unregister: unregister,
        val: function(v) {
            if (v !== undefined) {
                setValue(v)
            }
            return value
        },
    }
}
