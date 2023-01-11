function createAudioPlayer(player) {
    var playerParent = player.parentElement
    if (!playerParent) return function() {}

    function timeString(t) {
        var m = Math.floor(t / 60)
        var s = Math.floor(t % 60)
        return ("00" + m).slice(-2) + ":" + ("00" + s).slice(-2)
    }

    var root = document.createElement("div")
    root.className = "audio"

    var playpause = document.createElement("div")
    playpause.className = "audio__item audio__button audio__playpause"
    root.appendChild(playpause)

    var playpauseIcon = document.createElement("span")
    playpauseIcon.className = "icon icon--play"
    playpause.appendChild(playpauseIcon)

    var current = document.createElement("div")
    current.className = "audio__item audio__time"
    current.textContent = "00:00"
    root.appendChild(current)

    var controlContainer = document.createElement("div")
    controlContainer.className = "audio__item audio__slider audio__slider--control"
    root.appendChild(controlContainer)

    var wasPlaying = true
    var ended = true

    var controlSlider = createRangeSlider({
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
                var v = (val * player.duration) / 1000
                if (v === v) player.currentTime = v
            }
        },
    })

    controlContainer.appendChild(controlSlider.element)

    var total = document.createElement("div")
    total.className = "audio__item audio__time"
    total.textContent = player.readyState ? timeString(player.duration) : "00:00"
    root.appendChild(total)

    var volumeSlider

    if (!isMobile && !isTablet) {
        var volume = document.createElement("div")
        volume.className = "audio__item audio__button audio__volume"
        root.appendChild(volume)

        var volumeIcon = document.createElement("span")
        volumeIcon.className = "icon icon--volume-high"
        volume.appendChild(volumeIcon)

        var volumeContainer = document.createElement("div")
        volumeContainer.className = "audio__item audio__slider audio__slider--volume"
        root.appendChild(volumeContainer)

        var prevVolume = 0
        volumeSlider = createRangeSlider({
            max: 1,
            value: 1,
            onChange(val) {
                if (val === 0) {
                    volumeIcon.className = "icon icon--volume-mute"
                } else if (val < 0.3) {
                    volumeIcon.className = "icon icon--volume-low"
                } else if (val < 0.7) {
                    volumeIcon.className = "icon icon--volume-medium"
                } else {
                    volumeIcon.className = "icon icon--volume-high"
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

        volume.addEventListener("click", function() {
            if (!volumeSlider) return
            var v = volumeSlider.val()
            if (v) {
                prevVolume = v
                volumeSlider.val(0)
            } else {
                volumeSlider.val(prevVolume || 1)
            }
        })
    } else {
        player.volume = 1
    }

    player.addEventListener("timeupdate", function() {
        var currentTime = player.currentTime
        var duration = player.duration
        current.textContent = timeString(currentTime)
        if (!player.paused) {
            controlSlider.val((currentTime * 1000) / duration)
        }
    })

    player.addEventListener("ended", function() {
        pause()
        controlSlider.val(1000)
        ended = true
    })

    player.addEventListener("loadedmetadata", function() {
        total.textContent = timeString(player.duration)
    })

    function play() {
        playpauseIcon.className = "icon icon--pause"
        player.play()
        ended = false
    }

    function pause() {
        playpauseIcon.className = "icon icon--play"
        player.pause()
    }

    playpause.addEventListener("click", function() {
        if (player.readyState) {
            if (player.paused) {
                play()
            } else {
                pause()
            }
        }
    })

    playerParent.insertBefore(root, player)

    return function() {
        controlSlider.unregister()
        if (volumeSlider) {
            volumeSlider.unregister()
        }
    }
}

var players = document.getElementsByClassName("audio__player")

var fns = new Array(players.length)

for (var i = 0, n = players.length; i < n; i += 1) {
    fns[i] = createAudioPlayer(players[i])
}
