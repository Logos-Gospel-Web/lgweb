function sendAnalytics() {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', location.href)
    xhr.setRequestHeader('lgweb', '1')
    xhr.send(document.referrer)
}

sendAnalytics()
