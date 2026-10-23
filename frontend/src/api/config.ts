
export const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
    throw new Error("The API's URL is not defined. Please add the URL as an env. variable. (VITE_API_URL)")
}