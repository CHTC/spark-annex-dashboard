
export function getAPIUrl() {
    if(typeof process != undefined && process.env.NODE_ENV != 'production') {
        return process.env.NEXT_PUBLIC_API_URL
    } else if (typeof location !== 'undefined') {
        return `${location.protocol}//${location.host}/api/`
    } else {
        return ''
    }

}
