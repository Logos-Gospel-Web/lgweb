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
    const navThreshold = env.navThreshold || '960px'
    return {
        cache: false,
        mode: argv.mode,
        devtool: isProduction ? false : 'inline-cheap-source-map',
        output: {
            path: outputPath,
            publicPath: '/',
            chunkFormat: false,
        },
        watchOptions: {
            poll: 500,
        },
        resolve: {
            extensions: [
                '.js',
                '.ts',
                '.jsx',
                '.tsx',
                '.json',
                '.css',
                '.scss',
                '.sass',
            ],
        },
        module: {
            rules: [
                {
                    test: /\.[jt]sx?$/,
                    exclude: /node_modules/,
                    loader: 'builtin:swc-loader',
                    /** @type {import('@rspack/core').SwcLoaderOptions} */
                    options: {
                        jsc: {
                            loose: true,
                            assumptions: jsAssumptions,
                            transform: {
                                react: {
                                    runtime: 'automatic',
                                },
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
                            const relativePath = path
                                .relative(rootContext, resourcePath)
                                .replaceAll('\\', '/')

                            if (relativePath === 'styles/index.scss') {
                                return `$nav-threshold: ${navThreshold}; ${content}`
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
