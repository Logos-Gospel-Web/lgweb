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
