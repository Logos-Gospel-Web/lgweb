const languages = ['tc', 'sc']
const langRe = new RegExp(`^/(${languages.join('|')})(?:/|$)`)
const version = self.location.search
const cacheName = 'lgweb-' + version

function toErrorPage(lang: string) {
    return `/${lang}/error/400`
}

self.addEventListener('install', (ev: ExtendableEvent) => {
    ev.waitUntil(
        (async () => {
            const cache = await caches.open(cacheName)
            await Promise.all(
                languages.map(async (lang) => {
                    const url = toErrorPage(lang)
                    const errorPage = await fetch(url)
                    cache.put(url, errorPage)
                }),
            )
            console.log('[Service Worker] Installed')
        })(),
    )
})

self.addEventListener('fetch', (ev: FetchEvent) => {
    ev.respondWith(
        (async () => {
            const cache = await caches.open(cacheName)
            try {
                const resp = await fetch(ev.request)
                if (resp.ok) {
                    cache.put(ev.request, resp.clone())
                    return resp
                }
            } catch (err) {
                const cached = await cache.match(ev.request)
                if (cached) {
                    return cached
                }
            }
            const url = new URL(ev.request.url)
            const match = url.pathname.match(langRe)
            if (match) {
                const errorPage = await cache.match(toErrorPage(match[1]))
                if (errorPage) return errorPage
            }
            return new Response('', { status: 404 })
        })(),
    )
})
