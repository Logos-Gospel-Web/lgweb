import { defineConfig } from '@rspack/cli'
import { Compilation } from '@rspack/core'
import path from 'node:path'

const CSS_EXT = ['.css', '.scss', '.sass']

/** @type {import('@rspack/core').RspackPluginFunction} */
const NoEmitCssPlugin = (compiler) => {
    const name = 'NoEmitCssPlugin'
    compiler.hooks.thisCompilation.tap(name, (compilation) => {
        compilation.hooks.processAssets.tap(
            {
                name,
                stage: Compilation.PROCESS_ASSETS_STAGE_ADDITIONAL,
            },
            () => {
                for (const [key, entry] of compilation.entries.entries()) {
                    for (const dep of entry.dependencies) {
                        const ext = path.extname(dep.request)
                        if (CSS_EXT.includes(ext)) {
                            compilation.deleteAsset(key + '.js')
                            break
                        }
                    }
                }
            },
        )
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
            script: './app/scripts/index.ts',
            sw: './app/scripts/service.worker.ts',
            style: './app/styles/index.scss',
            richtext: './app/styles/richtext.scss',
            noscript: './app/styles/noscript.scss',
            error: './app/styles/error.scss',
            statistics: './app/styles/statistics.scss',
        },
        output: {
            path: outputPath,
            publicPath: '/',
        },
        watchOptions: {
            poll: 500,
        },
        resolve: {
            extensions: ['.js', '.ts', '.json', ...CSS_EXT],
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

                            if (relativePath === 'app/styles/index.scss') {
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
        plugins: [{ apply: NoEmitCssPlugin }],
        optimization: {
            splitChunks: false,
        },
        experiments: {
            css: true,
            rspackFuture: { bundlerInfo: { force: false } },
        },
    }
})
