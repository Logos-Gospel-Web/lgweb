const path = require('path')

function resolve(...args) {
    return path.resolve(__dirname, '..', '..', ...args)
}

const mode = process.env.MODE

const isDev = mode !== 'production'

const cacheDir =
    isDev && process.env.CACHE_DIR
        ? resolve(process.env.CACHE_DIR, 'webpack')
        : false

/** @type {import('webpack').Configuration} */
module.exports = {
    target: ['web', 'es5'],
    mode: mode,
    output: {
        globalObject: 'window',
    },
    cache: cacheDir
        ? {
              type: 'filesystem',
              cacheDirectory: cacheDir,
          }
        : false,
    resolve: {
        extensions: ['.js', '.ts', '.json'],
        alias: {
            '@': resolve('app', 'static', 'scripts'),
        },
    },
    module: {
        rules: [
            {
                test: /\.[tj]s/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
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
                    },
                },
            },
        ],
    },
}
