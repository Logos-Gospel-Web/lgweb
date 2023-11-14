module.exports = {
    presets: [
        [
            '@babel/preset-env',
            {
                useBuiltIns: false,
                targets: {
                    ie: 11,
                    chrome: 60,
                    safari: 10,
                    firefox: 43,
                    edge: 13,
                    opera: 37,
                    ios: 10,
                    samsung: 5,
                },
            },
        ],
        '@babel/preset-typescript',
    ],
    assumptions: {
        constantReexports: true,
        ignoreFunctionLength: true,
        ignoreToPrimitiveHint: true,
        iterableIsArray: true,
        noDocumentAll: true,
        noIncompleteNsImportDetection: true,
        noNewArrows: true,
        objectRestNoSymbols: true,
        setComputedProperties: true,
        setSpreadProperties: true,
    },
}
