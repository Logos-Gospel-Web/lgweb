const xhr = new XMLHttpRequest()
xhr.open('POST', '/view')
xhr.setRequestHeader('lgweb', '1')
xhr.send(location.pathname + ',' + document.referrer)
