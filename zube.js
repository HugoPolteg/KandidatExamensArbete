const dotenv = require('dotenv');
dotenv.config();

var fs = require('fs');
var jsonwebtoken = require('jsonwebtoken'); // $ npm install jsonwebtoken

const client_id = process.env.ZUBE_CLIENT_ID;
var private_key = fs.readFileSync("zube_api_key.pem");

var now = Math.floor(Date.now() / 1000);
var refresh_jwt = jsonwebtoken.sign({
    iat: now,      // Issued at time
    exp: now + 60, // JWT expiration time (10 minute maximum)
    iss: client_id // Your Zube client id
}, private_key, { algorithm: 'RS256' });

async function refreshToken(refresh_jwt, client_id) {
  try {
    const res = await fetch("https://zube.io/api/users/tokens", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + refresh_jwt,
        "X-Client-ID": client_id,
        "Accept": "application/json"
      }
    });

    console.log("Status:", res.status);

    const data = await res.json();
    console.log("Response:", data);
    return data.access_token
  } catch (err) {
    console.error("Error:", err);
  }
}

async function getProjects(access_jwt, client_id) {
  try {
    const res = await fetch("https://zube.io/api/projects", {
      method: "GET", 
      headers: {
        "Authorization": "Bearer " + access_jwt,
        "X-Client-ID": client_id,
        "Accept": "application/json"
      }
    });

    console.log("Status:", res.status);

    const data = await res.json();
    console.log("Response:", data);
    return data; // returnerar hela JSON-responsen
  } catch (err) {
    console.error("Error:", err);
  }
}

async function main() {
    var access_token = await refreshToken(refresh_jwt, client_id);
    console.log(access_token)
    getProjects(access_token, client_id)
}
main()