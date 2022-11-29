import axios from 'axios'


const signup = async(body) => {
    return await axios.post('http://localhost:8000/api/signup', body)
}


export default signup;