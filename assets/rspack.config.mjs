import { defineConfig } from '@rspack/cli'
import path from 'node:path'

/** @type {import('@rspack/core').RspackPluginFunction} */
const NoEmitJsPlugin = (compiler) => {
    const name = 'NoEmitJsPlugin'
    compiler.hooks.thisCompilation.tap(name, (compilation) => {
        compilation.hooks.chunkAsset.tap(name, (chunk, assetName) => {
            if (assetName.endsWith('.js')) {
                const modules = compilation.chunkGraph.getChunkModules(chunk)
                if (
                    modules.every((mod) => !mod.type.startsWith('javascript/'))
                ) {
                    compilation.deleteAsset(assetName)
                }
            }
        })
    })
}

/** @type {import('@rspack/core').SwcLoaderJscConfig['assumptions']} */
const jsAssumptions = {
    constantReexports: true,
    constantSuper: true,
    enumerableModuleMeta: true,
    ignoreFunctionLength: true,
    ignoreFunctionName: true,
    ignoreToPrimitiveHint: true,
    iterableIsArray: true,
    mutableTemplateObject: true,
    noClassCalls: true,
    noDocumentAll: true,
    noIncompleteNsImportDetection: true,
    noNewArrows: true,
    objectRestNoSymbols: true,
    privateFieldsAsProperties: true,
    pureGetters: true,
    setClassMethods: true,
    setComputedProperties: true,
    setPublicClassFields: true,
    setSpreadProperties: true,
    skipForOfIteratorClosing: true,
    superIsCallableConstructor: true,
}

export default defineConfig((env, argv) => {
    const isProduction = argv.mode === 'production'
    const outputPath = path.resolve(env.output || 'dist')
    return {
        cache: false,
        mode: argv.mode,
        devtool: isProduction ? false : false,
        entry: {
            script: './scripts/index.ts',
            sw: './scripts/service.worker.ts',
            style: './styles/index.scss',
            richtext: './styles/richtext.scss',
            noscript: './styles/noscript.scss',
            error: './styles/error.scss',
            statistics: './styles/statistics.scss',
        },
        output: {
            path: outputPath,
            publicPath: '/',
        },
        watchOptions: {
            poll: 500,
        },
        resolve: {
            extensions: ['.js', '.ts', '.json', '.css', '.scss', '.sass'],
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    loader: 'builtin:swc-loader',
                    /** @type {import('@rspack/core').SwcLoaderOptions} */
                    options: {
                        jsc: {
                            loose: true,
                            assumptions: jsAssumptions,
                            parser: {
                                syntax: 'ecmascript',
                            },
                        },
                    },
                    type: 'javascript/auto',
                },
                {
                    test: /\.ts$/,
                    exclude: /node_modules/,
                    loader: 'builtin:swc-loader',
                    /** @type {import('@rspack/core').SwcLoaderOptions} */
                    options: {
                        jsc: {
                            loose: true,
                            assumptions: jsAssumptions,
                            parser: {
                                syntax: 'typescript',
                            },
                        },
                    },
                    type: 'javascript/auto',
                },
                {
                    test: /\.(sass|scss)$/,
                    loader: 'sass-loader',
                    options: {
                        api: 'modern-compiler',
                        additionalData: (content, loaderContext) => {
                            const { resourcePath, rootContext } = loaderContext
                            const relativePath = path.relative(
                                rootContext,
                                resourcePath,
                            )

                            if (relativePath === 'styles/index.scss') {
                                // TODO: replace header variable
                                // return content.replace(
                                //     '@use "./components/header";',
                                //     '@use "./components/header";',
                                // )
                            }

                            return content
                        },
                    },
                    type: 'css',
                },
            ],
        },
        plugins: [{ apply: NoEmitJsPlugin }],
        optimization: {
            splitChunks: false,
        },
        experiments: {
            css: true,
            rspackFuture: { bundlerInfo: { force: false } },
        },
    }
})
