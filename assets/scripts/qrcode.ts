import { memoize, times } from './common'

type Version = number

type Matrix = [
    array: Uint8Array,
    offset: (row: number, column: number) => number,
    size: number,
    version: Version,
]

/* eslint-disable @typescript-eslint/no-unused-vars */
const L = 0
const M = 1
const Q = 2
const H = 3
/* eslint-enable @typescript-eslint/no-unused-vars */

type ErrorLevel = typeof L | typeof M | typeof Q | typeof H

const LOG = new Uint8Array(256)
const EXP = new Uint8Array(256)

for (let exponent = 1, value = 1; exponent < 256; exponent++) {
    value = value > 127 ? (value << 1) ^ 285 : value << 1
    LOG[value] = exponent % 255
    EXP[exponent % 255] = value
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function debugMatrix(matrix: Matrix) {
    const [array, _offset, size] = matrix
    const output = []
    for (let row = 0; row < size; ++row) {
        output.push(
            Array.from(array.subarray(row * size, (row + 1) * size)).join(', '),
        )
    }
    console.log(output.join('\n'))
}

function mul(a: number, b: number) {
    return a && b ? EXP[(LOG[a]! + LOG[b]!) % 255]! : 0
}

function div(a: number, b: number) {
    return EXP[(LOG[a]! + LOG[b]! * 254) % 255]!
}

function polyMul(
    poly1: Uint8Array | number[],
    poly2: Uint8Array | number[],
): Uint8Array<ArrayBuffer> {
    const coeffs = new Uint8Array(poly1.length + poly2.length - 1)

    // Instead of executing all the steps in the example, we can jump to
    // computing the coefficients of the result
    for (let index = 0; index < coeffs.length; index++) {
        let coeff = 0
        for (let p1index = 0; p1index <= index; p1index++) {
            const p2index = index - p1index
            coeff ^= mul(poly1[p1index]!, poly2[p2index]!)
        }
        coeffs[index] = coeff
    }
    return coeffs
}

function polyRest(
    dividend: Uint8Array | number[],
    divisor: Uint8Array | number[],
): Uint8Array {
    const quotientLength = dividend.length - divisor.length + 1
    // Let's just say that the dividend is the rest right away
    let rest = new Uint8Array(dividend)
    for (let count = 0; count < quotientLength; count++) {
        // If the first term is 0, we can just skip this iteration
        if (rest[0]) {
            const factor = div(rest[0], divisor[0]!)
            const subtr = new Uint8Array(rest.length)
            subtr.set(polyMul(divisor, [factor]), 0)
            rest = rest.map((value, index) => value ^ subtr[index]!).slice(1)
        } else {
            rest = rest.slice(1)
        }
    }
    return rest
}

const getGeneratorPoly = memoize((degree: number) => {
    let lastPoly = new Uint8Array([1])
    for (let index = 0; index < degree; index++) {
        lastPoly = polyMul(lastPoly, new Uint8Array([1, EXP[index]!]))
    }
    return lastPoly
})

function getNewMatrix(version: Version): Matrix {
    const size = version * 4 + 17
    return [
        new Uint8Array(size * size),
        (row, column) => row * size + column,
        size,
        version,
    ]
}

function fillArea(
    matrix: Matrix,
    row: number,
    column: number,
    width: number,
    height: number,
    fill: number = 1,
) {
    const fillRow = new Uint8Array(width).fill(fill)
    const [array, offset] = matrix

    for (let index = row; index < row + height; index++) {
        array.set(fillRow, offset(index, column))
    }
}

const getModuleSequence = memoize((version: Version): [number, number][] => {
    const matrix = getNewMatrix(version)
    const [array, offset, size] = matrix

    // Finder patterns + divisors
    fillArea(matrix, 0, 0, 9, 9)
    fillArea(matrix, 0, size - 8, 8, 9)
    fillArea(matrix, size - 8, 0, 9, 8)
    // Alignment patterns
    const alignmentTracks = getAlignmentTracks(version)
    const lastTrack = alignmentTracks.length - 1
    alignmentTracks.forEach((row, rowIndex) => {
        alignmentTracks.forEach((column, columnIndex) => {
            // Skipping the alignment near the finder patterns
            if (
                (rowIndex === 0 &&
                    (columnIndex === 0 || columnIndex === lastTrack)) ||
                (columnIndex === 0 && rowIndex === lastTrack)
            ) {
                return
            }
            fillArea(matrix, row - 2, column - 2, 5, 5)
        })
    })
    // Timing patterns
    fillArea(matrix, 6, 9, version * 4, 1)
    fillArea(matrix, 9, 6, 1, version * 4)
    // Dark module
    array[offset(size - 8, 8)] = 1
    // Version info
    if (version > 6) {
        fillArea(matrix, 0, size - 11, 3, 6)
        fillArea(matrix, size - 11, 0, 6, 3)
    }

    let rowStep = -1
    let row = size - 1
    let column = size - 1
    const sequence: [number, number][] = []
    let index = 0
    while (column >= 0) {
        if (array[offset(row, column)] === 0) {
            sequence.push([row, column])
        }
        // Checking the parity of the index of the current module
        if (index & 1) {
            row += rowStep
            if (row === -1 || row === size) {
                rowStep = -rowStep
                row += rowStep
                column -= column === 7 ? 2 : 1
            } else {
                column++
            }
        } else {
            column--
        }
        index++
    }
    return sequence
})

const MASK_FNS = [
    (row: number, column: number) => ((row + column) & 1) === 0,
    (row: number, _column: number) => (row & 1) === 0,
    (row: number, column: number) => column % 3 === 0,
    (row: number, column: number) => (row + column) % 3 === 0,
    (row: number, column: number) =>
        (((row >> 1) + Math.floor(column / 3)) & 1) === 0,
    (row: number, column: number) =>
        ((row * column) & 1) + ((row * column) % 3) === 0,
    (row: number, column: number) =>
        ((((row * column) & 1) + ((row * column) % 3)) & 1) === 0,
    (row: number, column: number) =>
        ((((row + column) & 1) + ((row * column) % 3)) & 1) === 0,
]

function getMaskedMatrix(
    version: Version,
    codewords: Uint8Array,
    maskIndex: number,
) {
    const sequence = getModuleSequence(version)
    const matrix = getNewMatrix(version)
    const [array, offset] = matrix
    sequence.forEach(([row, column], index) => {
        // Each codeword contains 8 modules, so shifting the index to the
        // right by 3 gives the codeword's index
        const codeword = codewords[index >> 3]!
        const bitShift = 7 - (index & 7)
        const moduleBit = (codeword >> bitShift) & 1
        array[offset(row, column)] =
            moduleBit ^ +MASK_FNS[maskIndex]!(row, column)
    })
    return matrix
}

const FORMAT_DIVISOR = new Uint8Array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1])
const FORMAT_MASK = new Uint8Array([
    1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0,
])

function getFormatModules(errorLevel: ErrorLevel, maskIndex: number) {
    const formatPoly = new Uint8Array(15)
    formatPoly[0] = errorLevel >> 1
    formatPoly[1] = ~errorLevel & 1
    formatPoly[2] = maskIndex >> 2
    formatPoly[3] = (maskIndex >> 1) & 1
    formatPoly[4] = maskIndex & 1
    const rest = polyRest(formatPoly, FORMAT_DIVISOR)
    formatPoly.set(rest, 5)
    const maskedFormatPoly = formatPoly.map(
        (bit, index) => bit ^ FORMAT_MASK[index]!,
    )
    return maskedFormatPoly
}

function placeFinderPatterns(matrix: Matrix, row: number, column: number) {
    fillArea(matrix, row, column, 7, 7)
    fillArea(matrix, row + 1, column + 1, 5, 5, 0)
    fillArea(matrix, row + 2, column + 2, 3, 3)
}

function placeFixedPatterns(matrix: Matrix) {
    const [array, offset, size, version] = matrix
    // Finder patterns
    placeFinderPatterns(matrix, 0, 0)
    placeFinderPatterns(matrix, size - 7, 0)
    placeFinderPatterns(matrix, 0, size - 7)
    // Separators
    // fillArea(matrix, 7, 0, 8, 1, 0)
    // fillArea(matrix, 0, 7, 1, 7, 0)
    // fillArea(matrix, size - 8, 0, 8, 1, 0)
    // fillArea(matrix, 0, size - 8, 1, 7, 0)
    // fillArea(matrix, 7, size - 8, 8, 1, 0)
    // fillArea(matrix, size - 7, 7, 1, 7, 0)
    // Alignment patterns
    const alignmentTracks = getAlignmentTracks(version)
    const lastTrack = alignmentTracks.length - 1
    alignmentTracks.forEach((row, rowIndex) => {
        alignmentTracks.forEach((column, columnIndex) => {
            // Skipping the alignment near the finder patterns
            if (
                (rowIndex === 0 &&
                    (columnIndex === 0 || columnIndex === lastTrack)) ||
                (columnIndex === 0 && rowIndex === lastTrack)
            ) {
                return
            }
            fillArea(matrix, row - 2, column - 2, 5, 5)
            fillArea(matrix, row - 1, column - 1, 3, 3, 0)
            array[offset(row, column)] = 1
        })
    })
    // Timing patterns
    for (let pos = 8; pos <= size - 9; pos += 2) {
        array[offset(6, pos)] = 1
        array[offset(6, pos + 1)] = 0
        array[offset(pos, 6)] = 1
        array[offset(pos + 1, 6)] = 0
    }
    array[offset(6, size - 7)] = 1
    array[offset(size - 7, 6)] = 1
    // Dark module
    array[offset(size - 8, 8)] = 1
}

function placeFormatModules(
    matrix: Matrix,
    errorLevel: ErrorLevel,
    maskIndex: number,
) {
    const formatModules = getFormatModules(errorLevel, maskIndex)
    const [array, offset, size] = matrix

    array.set(formatModules.subarray(0, 6), offset(8, 0))
    array.set(formatModules.subarray(6, 8), offset(8, 7))
    array.set(formatModules.subarray(7), offset(8, size - 8))
    array[offset(7, 8)] = formatModules[8]!

    formatModules
        .subarray(0, 7)
        .forEach((cell, index) => (array[offset(size - index - 1, 8)] = cell))
    formatModules
        .subarray(9)
        .forEach((cell, index) => (array[offset(5 - index, 8)] = cell))
}

function getMaskedQRCode(
    version: Version,
    codewords: Uint8Array,
    errorLevel: ErrorLevel,
    maskIndex: number,
) {
    const matrix = getMaskedMatrix(version, codewords, maskIndex)
    placeFormatModules(matrix, errorLevel, maskIndex)
    placeFixedPatterns(matrix)
    placeVersionModules(matrix)
    return matrix
}

function getRule1Penalty(
    array: Uint8Array,
    offset: number,
    step: number,
    total: number,
) {
    let count = 0
    let counting = 0
    let penalty = 0
    for (let i = offset, len = offset + step * total; i < len; i += step) {
        const cell = array[i]!
        if (cell !== counting) {
            counting = cell
            count = 1
        } else {
            count++
            if (count === 5) {
                penalty += 3
            } else if (count > 5) {
                penalty++
            }
        }
    }
    return penalty
}

const RULE_3_PATTERN = new Uint8Array([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0])
const RULE_3_REVERSED_PATTERN = RULE_3_PATTERN.slice().reverse()
const RULE_3_SIZE = RULE_3_PATTERN.length

function getRule3Penalty(array: Uint8Array, offset: number, step: number) {
    const pattern =
        array[offset]! === 1 ? RULE_3_PATTERN : RULE_3_REVERSED_PATTERN
    for (let i = offset + step, p = 1; p < RULE_3_SIZE; i += step, ++p) {
        const cell = array[i]!
        if (cell !== pattern[p]) {
            return 0
        }
    }
    return 40
}

function getPenaltyScore(matrix: Matrix) {
    const [array, offset, size] = matrix

    let totalPenalty = 0
    const totalModules = array.length

    // Rule 1
    for (let i = 0; i < size; ++i) {
        totalPenalty += getRule1Penalty(array, i * size, 1, size) // row penalty
        totalPenalty += getRule1Penalty(array, i, size, size) // column penalty
    }

    // Rule 2
    for (let row = 1; row < size; ++row) {
        for (let column = 1; column < size; ++column) {
            const i = offset(row, column)
            const cell = array[i]!
            if (
                cell === array[i - 1]! &&
                cell === array[i - size]! &&
                cell === array[i - size - 1]!
            ) {
                totalPenalty += 3
            }
        }
    }

    // Rule 3
    for (let i = 0, len = size - RULE_3_SIZE; i <= len; ++i) {
        for (let j = 0; j < size; ++j) {
            totalPenalty += getRule3Penalty(array, offset(j, i), 1) // row penalty
            totalPenalty += getRule3Penalty(array, offset(i, j), size) // column penalty
        }
    }

    // Rule 4
    const darkModules = array.reduce((sum, cell) => sum + cell, 0)
    const percentage = (darkModules * 100) / totalModules
    totalPenalty += Math.abs(Math.trunc(percentage / 5 - 10)) * 10

    return totalPenalty
}

function getOptimalMask(
    version: Version,
    codewords: Uint8Array,
    errorLevel: ErrorLevel,
) {
    let bestMatrix
    let bestScore = Infinity
    for (let index = 0; index < 8; index++) {
        const matrix = getMaskedQRCode(version, codewords, errorLevel, index)
        const penaltyScore = getPenaltyScore(matrix)
        if (penaltyScore < bestScore) {
            bestScore = penaltyScore
            bestMatrix = matrix
        }
    }
    return bestMatrix!
}

// byte mode
function getData(
    content: string,
    lengthBits: number,
    dataCodewords: number,
): Uint8Array {
    const textLength = content.length
    const rightShift = (4 + lengthBits) & 7
    const leftShift = 8 - rightShift
    const andMask = (1 << rightShift) - 1

    const data = new Uint8Array(dataCodewords)

    let i = 0
    data[i++] = (0b0100 << 4) + (textLength >> (lengthBits - 4))
    if (lengthBits > 12) {
        data[i++] = (textLength >> rightShift) & 0xff
    }
    data[i] = (textLength & andMask) << leftShift

    for (let j = 0; j < textLength; ++j) {
        const byte = content.charCodeAt(j)
        data[i]! |= byte >> rightShift
        data[++i] = (byte & andMask) << leftShift
    }

    let fill = 17
    for (; i < data.length; ) {
        data[++i] = fill = 253 - fill
    }
    return data
}

function getLengthBits(version: Version): number {
    return version > 9 ? 16 : 8 // byte mode
}

const getAlignmentTracks = memoize((version: Version): number[] => {
    if (version === 1) {
        return []
    }
    const intervals = Math.floor(version / 7) + 1
    const distance = 4 * version + 4 // between first and last pattern
    const step = Math.ceil(distance / intervals / 2) * 2
    return [6].concat(
        times(
            intervals,
            (index) => distance + 6 - (intervals - 1 - index) * step,
        ),
    )
})

const getAvailableModules = memoize((version: Version) => {
    if (version === 1) {
        return 21 * 21 - 3 * 8 * 8 - 2 * 15 - 1 - 2 * 5
    }
    const alignmentCount = Math.floor(version / 7) + 2
    return (
        (version * 4 + 17) ** 2 -
        3 * 8 * 8 -
        (alignmentCount ** 2 - 3) * 5 * 5 -
        2 * (version * 4 + 1) +
        (alignmentCount - 2) * 5 * 2 -
        2 * 15 -
        1 -
        (version > 6 ? 2 * 3 * 6 : 0)
    )
})

function getDataCodewords(version: Version, errorLevel: ErrorLevel) {
    const totalCodewords = getAvailableModules(version) >> 3
    const [blocks, ecBlockSize] = EC_TABLE[version - 1]![errorLevel]
    return totalCodewords - blocks * ecBlockSize
}

function getCapacity(version: Version, errorLevel: ErrorLevel) {
    const dataCodewords = getDataCodewords(version, errorLevel)
    const lengthBits = getLengthBits(version)
    const availableBits = (dataCodewords << 3) - lengthBits - 4
    return availableBits >> 3 // byte mode
}

function getVersionAndErrorLevel(
    contentLength: number,
    minErrorLevel: ErrorLevel,
): [number, ErrorLevel] {
    for (let version = 1; version <= 40; version++) {
        for (let i = H; i >= minErrorLevel; --i) {
            const errorLevel = i as ErrorLevel
            const capacity = getCapacity(version, errorLevel)
            if (capacity >= contentLength) {
                return [version, errorLevel]
            }
        }
    }
    throw 0
}

function reorderData(data: Uint8Array, totalBlocks: number) {
    const group1Blocks = totalBlocks - (data.length % totalBlocks)
    const group1Size = Math.floor(data.length / totalBlocks)
    const group2Size = group1Size + 1

    const blockIndexes = new Array(totalBlocks)
    blockIndexes[0] = 0

    for (let i = 1; i < totalBlocks; ++i) {
        blockIndexes[i] =
            blockIndexes[i - 1]! + (i < group1Blocks ? group1Size : group2Size)
    }

    let b = 0
    const array = new Uint8Array(data.length)
    for (let i = 0; i < data.length; ++i) {
        array[i] = data[blockIndexes[b]++]!
        b = (b + 1) % totalBlocks
    }

    return array
}

function getECDataForBlock(
    data: Uint8Array,
    offset: number,
    length: number,
    ecSize: number,
) {
    const messagePoly = new Uint8Array(length + ecSize)
    messagePoly.set(data.subarray(offset, offset + length), 0)
    return polyRest(messagePoly, getGeneratorPoly(ecSize))
}

function getECData(data: Uint8Array, totalBlocks: number, ecBlockSize: number) {
    const group1Blocks = totalBlocks - (data.length % totalBlocks)
    const group1Size = Math.floor(data.length / totalBlocks)
    const group2Size = group1Size + 1

    let blockIndex = 0

    const array = new Uint8Array(ecBlockSize * totalBlocks)
    for (let i = 0; i < totalBlocks; ++i) {
        const blockSize = i < group1Blocks ? group1Size : group2Size
        const ecData = getECDataForBlock(
            data,
            blockIndex,
            blockSize,
            ecBlockSize,
        )
        ecData.forEach((cell, index) => {
            array[index * totalBlocks + i] = cell
        })
        blockIndex += blockSize
    }

    return array
}

function getCodewords(content: string, minErrorLevel: ErrorLevel) {
    const [version, errorLevel] = getVersionAndErrorLevel(
        content.length,
        minErrorLevel,
    )
    const lengthBits = getLengthBits(version)

    const dataCodewords = getDataCodewords(version, errorLevel)
    const [ecBlockSize, blocks] = EC_TABLE[version - 1]![errorLevel]

    const rawData = getData(content, lengthBits, dataCodewords)
    const data = reorderData(rawData, blocks)
    const ecData = getECData(rawData, blocks, ecBlockSize)

    const codewords = new Uint8Array(data.length + ecData.length)
    codewords.set(data, 0)
    codewords.set(ecData, data.length)

    return [codewords, version, errorLevel] as const
}

const VERSION_DIVISOR = new Uint8Array([1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1])
const getVersionInformation = memoize((version: Version) => {
    const poly = new Uint8Array(18)
    const binary = version.toString(2).padStart(6, '0')
    for (let i = 0; i < 6; ++i) {
        poly[i] = +binary[i]!
    }
    poly.set(polyRest(poly, VERSION_DIVISOR), 6)
    return poly
})

function placeVersionModules(matrix: Matrix) {
    const [array, offset, size, version] = matrix
    if (version < 7) {
        return
    }
    getVersionInformation(version).forEach((bit, index) => {
        const row = Math.floor(index / 3)
        const col = index % 3
        array[offset(5 - row, size - 9 - col)] = bit
        array[offset(size - 11 + col, row)] = bit
    })
}

function printMatrix(matrix: Matrix) {
    const [array, offset, size] = matrix
    const canvas = document.createElement('canvas')
    const scale = 64
    canvas.width = canvas.height = (size + 2) * scale
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#000'

    for (let row = 0; row < size; ++row) {
        for (let col = 0; col < size; ++col) {
            if (array[offset(row, col)]) {
                ctx.fillRect((col + 1) * scale, (row + 1) * scale, scale, scale)
            }
        }
    }

    return canvas
}

export function getQRCode(content: string): HTMLElement {
    const [codewords, version, errorLevel] = getCodewords(content, L)
    const matrix = getOptimalMask(version, codewords, errorLevel)

    return printMatrix(matrix)
}

export {
    getData,
    getECData,
    getECDataForBlock,
    getGeneratorPoly,
    getModuleSequence,
}

const EC_TABLE: [
    [number, number],
    [number, number],
    [number, number],
    [number, number],
][] = [
    [
        [7, 1],
        [10, 1],
        [13, 1],
        [17, 1],
    ],
    [
        [10, 1],
        [16, 1],
        [22, 1],
        [28, 1],
    ],
    [
        [15, 1],
        [26, 1],
        [18, 2],
        [22, 2],
    ],
    [
        [20, 1],
        [18, 2],
        [26, 2],
        [16, 4],
    ],
    [
        [26, 1],
        [24, 2],
        [18, 4],
        [22, 4],
    ],
    [
        [18, 2],
        [16, 4],
        [24, 4],
        [28, 4],
    ],
    [
        [20, 2],
        [18, 4],
        [18, 6],
        [26, 5],
    ],
    [
        [24, 2],
        [22, 4],
        [22, 6],
        [26, 6],
    ],
    [
        [30, 2],
        [22, 5],
        [20, 8],
        [24, 8],
    ],
    [
        [18, 4],
        [26, 5],
        [24, 8],
        [28, 8],
    ],
    [
        [20, 4],
        [30, 5],
        [28, 8],
        [24, 11],
    ],
    [
        [24, 4],
        [22, 8],
        [26, 10],
        [28, 11],
    ],
    [
        [26, 4],
        [22, 9],
        [24, 12],
        [22, 16],
    ],
    [
        [30, 4],
        [24, 9],
        [20, 16],
        [24, 16],
    ],
    [
        [22, 6],
        [24, 10],
        [30, 12],
        [24, 18],
    ],
    [
        [24, 6],
        [28, 10],
        [24, 17],
        [30, 16],
    ],
    [
        [28, 6],
        [28, 11],
        [28, 16],
        [28, 19],
    ],
    [
        [30, 6],
        [26, 13],
        [28, 18],
        [28, 21],
    ],
    [
        [28, 7],
        [26, 14],
        [26, 21],
        [26, 25],
    ],
    [
        [28, 8],
        [26, 16],
        [30, 20],
        [28, 25],
    ],
    [
        [28, 8],
        [26, 17],
        [28, 23],
        [30, 25],
    ],
    [
        [28, 9],
        [28, 17],
        [30, 23],
        [24, 34],
    ],
    [
        [30, 9],
        [28, 18],
        [30, 25],
        [30, 30],
    ],
    [
        [30, 10],
        [28, 20],
        [30, 27],
        [30, 32],
    ],
    [
        [26, 12],
        [28, 21],
        [30, 29],
        [30, 35],
    ],
    [
        [28, 12],
        [28, 23],
        [28, 34],
        [30, 37],
    ],
    [
        [30, 12],
        [28, 25],
        [30, 34],
        [30, 40],
    ],
    [
        [30, 13],
        [28, 26],
        [30, 35],
        [30, 42],
    ],
    [
        [30, 14],
        [28, 28],
        [30, 38],
        [30, 45],
    ],
    [
        [30, 15],
        [28, 29],
        [30, 40],
        [30, 48],
    ],
    [
        [30, 16],
        [28, 31],
        [30, 43],
        [30, 51],
    ],
    [
        [30, 17],
        [28, 33],
        [30, 45],
        [30, 54],
    ],
    [
        [30, 18],
        [28, 35],
        [30, 48],
        [30, 57],
    ],
    [
        [30, 19],
        [28, 37],
        [30, 51],
        [30, 60],
    ],
    [
        [30, 19],
        [28, 38],
        [30, 53],
        [30, 63],
    ],
    [
        [30, 20],
        [28, 40],
        [30, 56],
        [30, 66],
    ],
    [
        [30, 21],
        [28, 43],
        [30, 59],
        [30, 70],
    ],
    [
        [30, 22],
        [28, 45],
        [30, 62],
        [30, 74],
    ],
    [
        [30, 24],
        [28, 47],
        [30, 65],
        [30, 77],
    ],
    [
        [30, 25],
        [28, 49],
        [30, 68],
        [30, 81],
    ],
]
