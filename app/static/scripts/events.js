function listen(elem, event, listener, passive) {
    var options = supportPassiveListener && passive !== undefined ? { passive } : false
    elem.addEventListener(event, listener, options)
    return function() {
        elem.removeEventListener(event, listener, false)
    }
}

// Stop propagation does not work here
function delegate(selector, event, listener, passive) {
    var fn = function(evt) {
        var el = evt.target

        if (el) {
            el = el.closest(selector)
            if (el) {
                var newEvt = Object.create(evt)
                Object.defineProperties(newEvt, {
                    target: { value: evt.target },
                    currentTarget: { value: el },
                    preventDefault: { value: function() { evt.preventDefault() } },
                })
                listener(newEvt)
            }
        }
    }
    return listen(document.body, event, fn, passive)
}
