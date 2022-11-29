import axios from 'axios'


const login = async(body) => {
    return await axios.post('http://localhost:8000/api/login', body)
}


export default login;