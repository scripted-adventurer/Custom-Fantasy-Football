export function requestOptions(method) {
  let options = {'method': method, 'credentials': 'include'};
  if (method !== 'GET') {
    options.headers = {'Content-Type': 'application/json'};
    options.body = {};
  }
  return options;
}