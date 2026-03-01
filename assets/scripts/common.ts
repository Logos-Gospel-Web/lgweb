export function noop() {}

export function memoize<T extends (arg: any) => any>(fn: T): T {
    const cache: Record<keyof any, any> = {}
    return ((arg: any): any => {
        if (arg in cache) {
            return cache[arg]
        }
        return (cache[arg] = fn(arg))
    }) as any
}

export function times<T>(count: number, fn: (index: number) => T): T[] {
    const output: T[] = []
    for (let i = 0; i < count; ++i) {
        output.push(fn(i))
    }
    return output
}
