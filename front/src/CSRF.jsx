import axios from 'axios';
import { serverUrl } from './components/Config.jsx'

export const getCsrfToken = () => {
    return axios.get(serverUrl + 'api/csrf/', {withCredentials: true})
        .then(response => {
            return response.headers['x-csrftoken'];
        })
};