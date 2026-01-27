export const getAPIUrl = () => typeof location !== 'undefined' ? `${location.protocol}//${location.host}/api/` : '';
