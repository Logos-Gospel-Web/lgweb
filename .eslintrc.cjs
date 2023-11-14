module.exports = {
    extends: ['eslint:recommended', 'plugin:prettier/recommended'],
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint'],
    root: true,
    env: {
        node: true,
    },

    parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
    },

    ignorePatterns: ['dist'],

    rules: {
        'prettier/prettier': [
            'error',
            {
                tabWidth: 4,
                semi: false,
                singleQuote: true,
                trailingComma: 'all',
            },
        ],
        eqeqeq: ['error', 'smart'],
        'no-unused-vars': [
            'error',
            {
                argsIgnorePattern: '^_',
                varsIgnorePattern: '^_',
                caughtErrorsIgnorePattern: '^_',
            },
        ],
    },

    overrides: [
        {
            files: ['app/**'],
            env: {
                browser: true,
                node: false,
            },
        },
        {
            files: ['**/*.ts'],
            extends: [
                'eslint:recommended',
                'plugin:@typescript-eslint/recommended',
                'plugin:prettier/recommended',
            ],
            rules: {
                '@typescript-eslint/no-explicit-any': 'off',
                'no-unused-vars': 'off',
                '@typescript-eslint/no-unused-vars': [
                    'error',
                    {
                        argsIgnorePattern: '^_',
                        varsIgnorePattern: '^_',
                        caughtErrorsIgnorePattern: '^_',
                    },
                ],
            },
        },
    ],
}
