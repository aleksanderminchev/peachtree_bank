import axios from "axios";
const HOST_API_KEY = import.meta.env["VITE_HOST_API_KEY"];
export const setSession = (accessToken: string | null) => {
  // If access token is not null
  console.log(accessToken);
  if (accessToken) {
    localStorage.setItem("accessToken", accessToken);
    sessionStorage.setItem("accessToken", accessToken);
    axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
  } else {
    localStorage.removeItem("accessToken");
    sessionStorage.removeItem("accessToken");
    delete axios.defaults.headers.common.Authorization;
  }
};

// ----------------------------------------------------------------------

/** creates a new instance of the Axios library with a specified configuration.
 * In this case, the configuration sets the baseURL property to HOST_API_KEY,
 * which is the base URL for all requests made using this Axios instance.
 */

const axiosInstance = axios.create({
  baseURL: HOST_API_KEY,
  withCredentials: true,
});
/** adds a request interceptor to the Axios instance.
 * This interceptor is a function that will be executed for every HTTP request received by the Axios instance.
 * The function takes two arguments: request and error.
 * If the request is successful, it returns the request object.
 * It adds the market_id to the request object
 * If the request contains an error. It returns a rejected Promise with the error data or a default error message.
 */
axiosInstance.interceptors.request.use(
  (config) => {
    config.withCredentials = true;
    console.log(config);
    return config;
  },
  async (error) => {
    // console.log('test');
    return Promise.reject((error.response && error.response.data) || error);
  }
);
/** adds a response interceptor to the Axios instance.
 * This interceptor is a function that will be executed for every HTTP response received by the Axios instance.
 * The function takes two arguments: response and error.
 * If the response is successful, it returns the response object.
 * If the response contains an error. If the error is a 401 authentication, we try to refresh the authentication token.
 * Otherwise it returns a rejected Promise with the error data or a default error message.
 */
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { status, config } = error?.response || {};

    // If there is an authentication error, we try to refresh the access token.

    if (status === 401 && config.url !== "/api/tokens") {
      const refreshResponse = await axiosInstance.put(
        "/api/tokens",
        {},
        {
          withCredentials: true, // Include with credentials so Refresh Token is send securely as a cookie
        }
      );
      const { access_token: accessToken } = refreshResponse.data;
      // Update local storage with new access token and axios default header or if access token is Null then remove the old access token from local storage
      setSession(accessToken);
      console.log("config");
      if (refreshResponse.status === 200) {
        // Ensure the retry request also has withCredentials set to true
        config.withCredentials = true;
        return axiosInstance.request(config);
      }

      return Promise.reject((error.response && error.response.data) || error);
    }
    return Promise.reject((error.response && error.response.data) || error);
  }
);

export default axiosInstance;
