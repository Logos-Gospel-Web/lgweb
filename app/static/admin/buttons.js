/**
 * @param {string} text
 * @param {() => void} onClick
 * @returns {HTMLElement}
 */
function lgwebButtonsCreateButton(text, onClick) {
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'grp-button'
    button.textContent = text
    button.onclick = onClick

    const div = document.createElement('div')
    div.appendChild(button)
    return div
}

function lgwebButtonsGetCsrfToken() {
    const element = document.querySelector('input[name=csrfmiddlewaretoken]')
    return element ? element.value : ''
}

function lgwebButtonsAddButtonsToForm() {
    const footer = document.querySelector('.grp-submit-row > div')
    if (!footer) return
    const publishFields = document.querySelectorAll(
        '#id_publish,[id^=id_children-][id$=-publish]',
    )
    if (publishFields.length) {
        footer.appendChild(
            lgwebButtonsCreateButton('Preview', async () => {
                const form = new URLSearchParams()
                form.append('csrfmiddlewaretoken', lgwebButtonsGetCsrfToken())
                const slug = document.querySelector('#id_slug')
                if (slug) {
                    form.append('slug', slug.value)
                } else {
                    const parent = document.querySelector('#id_parent')
                    const position = document.querySelector('#id_position')
                    if (parent && position) {
                        form.append('topic_id', parent.value)
                        form.append('position', position.value)
                    } else {
                        return
                    }
                }
                const resp = await fetch('/adminapi/preview', {
                    method: 'POST',
                    body: form,
                })
                if (!resp.ok) return
                const url = await resp.text()
                if (!url) return
                console.log(url)
                let maxPublish = ''
                publishFields.forEach((el) => {
                    if (
                        el instanceof HTMLInputElement &&
                        el.value > maxPublish
                    ) {
                        maxPublish = el.value
                    }
                })
                if (!maxPublish) return
                const maxPublishTime = Date.parse(
                    maxPublish + 'T00:00:00+08:00',
                )
                if (maxPublishTime < Date.now()) {
                    window.open(url)
                } else {
                    window.open(url + '?preview=' + maxPublish)
                }
            }),
        )
    }
}

document.addEventListener('DOMContentLoaded', lgwebButtonsAddButtonsToForm)
