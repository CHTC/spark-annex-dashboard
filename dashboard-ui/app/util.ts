/**
 * Util function to munge the API url that the frontend calls out to:
 * - In Development, specified by an environment variable
 * - In production, appending `/api` to the browser's current top-level domain
 * - During production builds, an empty string (as opposed to breaking the build with a null value)
 * @returns 
 */
export function getAPIUrl() {
    if(typeof process != undefined && process.env.NODE_ENV != 'production') {
        return process.env.NEXT_PUBLIC_API_URL
    } else if (typeof location !== 'undefined') {
        return `${location.protocol}//${location.host}/api/`
    } else {
        return ''
    }

}
