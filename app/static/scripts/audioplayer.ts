import { noop } from './common'
import { createRangeSlider } from './rangeslider'

function createAudioPlayer(player: HTMLAudioElement) {
    const playerParent = player.parentElement
    if (!playerParent) return noop

    function timeString(t: number) {
        const m = Math.floor(t / 60)
        const s = Math.floor(t % 60)
        return ('00' + m).slice(-2) + ':' + ('00' + s).slice(-2)
    }

    const root = document.createElement('div')
    root.className = 'audio'

    const playpause = document.createElement('div')
    playpause.className = 'audio__item audio__button audio__playpause'
    root.appendChild(playpause)

    const playpauseIcon = document.createElement('span')
    playpauseIcon.className = 'icon icon--play'
    playpause.appendChild(playpauseIcon)

    const current = document.createElement('div')
    current.className = 'audio__item audio__time'
    current.textContent = '00:00'
    root.appendChild(current)

    const controlContainer = document.createElement('div')
    controlContainer.className =
        'audio__item audio__slider audio__slider--control'
    root.appendChild(controlContainer)

    let wasPlaying = true
    let ended = true

    const controlSlider = createRangeSlider({
        max: 1000,
        onActive() {
            wasPlaying = !player.paused
            if (wasPlaying) {
                pause()
            }
        },
        onInactive(val) {
            if (ended) {
                ended = val >= 1000
                if (!ended) {
                    play()
                }
            }
            if (wasPlaying && !ended) {
                play()
            }
        },
        onChange(val) {
            if (player.paused) {
                const v = (val * player.duration) / 1000
                if (v === v) player.currentTime = v
            }
        },
    })

    controlContainer.appendChild(controlSlider.element)

    const total = document.createElement('div')
    total.className = 'audio__item audio__time'
    total.textContent = player.readyState
        ? timeString(player.duration)
        : '00:00'
    root.appendChild(total)

    const volume = document.createElement('div')
    volume.className = 'audio__item audio__button audio__volume'
    root.appendChild(volume)

    const volumeIcon = document.createElement('span')
    volumeIcon.className = 'icon icon--volume-high'
    volume.appendChild(volumeIcon)

    const volumeContainer = document.createElement('div')
    volumeContainer.className =
        'audio__item audio__slider audio__slider--volume'
    root.appendChild(volumeContainer)

    let prevVolume = 0
    const volumeSlider = createRangeSlider({
        max: 1,
        value: 1,
        onChange(val) {
            if (val === 0) {
                volumeIcon.className = 'icon icon--volume-mute'
            } else if (val < 0.3) {
                volumeIcon.className = 'icon icon--volume-low'
            } else if (val < 0.7) {
                volumeIcon.className = 'icon icon--volume-medium'
            } else {
                volumeIcon.className = 'icon icon--volume-high'
            }
            player.volume = val
        },
        onInactive(val) {
            if (val) {
                prevVolume = val
            }
        },
    })
    volumeContainer.appendChild(volumeSlider.element)

    volume.addEventListener('click', () => {
        const v = volumeSlider.val()
        if (v) {
            prevVolume = v
            volumeSlider.val(0)
        } else {
            volumeSlider.val(prevVolume || 1)
        }
    })

    player.addEventListener('timeupdate', () => {
        const currentTime = player.currentTime
        const duration = player.duration
        current.textContent = timeString(currentTime)
        if (!player.paused) {
            controlSlider.val((currentTime * 1000) / duration)
        }
    })

    player.addEventListener('ended', () => {
        pause()
        controlSlider.val(1000)
        ended = true
    })

    player.addEventListener('loadedmetadata', () => {
        total.textContent = timeString(player.duration)
    })

    function play() {
        playpauseIcon.className = 'icon icon--pause'
        player.play()
        ended = false
    }

    function pause() {
        playpauseIcon.className = 'icon icon--play'
        player.pause()
    }

    playpause.addEventListener('click', () => {
        if (player.readyState) {
            if (player.paused) {
                play()
            } else {
                pause()
            }
        }
    })

    playerParent.insertBefore(root, player)

    return () => {
        controlSlider.unregister()
        volumeSlider.unregister()
    }
}

const players = document.getElementsByClassName('audio__player')

const fns = new Array(players.length)

for (let i = 0, n = players.length; i < n; i += 1) {
    fns[i] = createAudioPlayer(players[i] as HTMLAudioElement)
}
