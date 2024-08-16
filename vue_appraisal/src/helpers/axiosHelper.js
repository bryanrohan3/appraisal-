import axios from "axios";
import store from "@/store";

const hostname = "http://localhost:8000/";

const apiConstants = {
  api_hostname: hostname + "api/",
  hostname: hostname,
};

const axiosInstance = axios.create({
  baseURL: apiConstants.api_hostname, // Your API base URL
});

let tokenType = "Token";

// Add a request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = store.getters.getAuthToken; // Get the token from your Vuex store
    if (token) {
      config.headers["Authorization"] = `${tokenType} ${token}`; // Set the token in the Authorization header
    } else {
      console.warn("No auth token found");
    }
    return config;
  },
  (error) => {
    return Promise.reject(error); // Pass the error to the next interceptor
  }
);

const endpoints = {
  login: apiConstants.api_hostname + "users/login/",
  dashboard_appraisals: apiConstants.api_hostname + "appraisals/simple-list/",
  top_wholesaler: apiConstants.api_hostname + "appraisals/top-wholesaler/",
  top_car: apiConstants.api_hostname + "appraisals/top-car/",
  createAppraisal: apiConstants.api_hostname + "appraisals/",
  dealerProfile: apiConstants.api_hostname + "dealer-profile/current/",
  all_appraisals: apiConstants.api_hostname + "appraisals/",
  appraisals: apiConstants.api_hostname + "appraisals/csv",
  makeWinner: (offerId) =>
    `${apiConstants.api_hostname}offer/${offerId}/make-winner/`,
  updateOffer: (appraisalId, offerId) =>
    `${apiConstants.api_hostname}appraisals/${appraisalId}/update_offer/${offerId}/`,
  addGeneralComment: (appraisalId) =>
    `${apiConstants.api_hostname}appraisals/${appraisalId}/add_general_comment/`,
  addPrivateComment: (appraisalId) =>
    `${apiConstants.api_hostname}appraisals/${appraisalId}/add_private_comment/`,
  getAppraisal: (id) => `${apiConstants.api_hostname}appraisals/${id}/`,
  mostCommonCarsByDateRange: () =>
    apiConstants.api_hostname + "appraisals/most_common_cars_by_date_range/",
  bestWholesalersByDateRange: () =>
    apiConstants.api_hostname + "appraisals/best-performing-wholesalers/",
  allCount: apiConstants.api_hostname + "appraisals/count/", // Add this line
  statusList: apiConstants.api_hostname + "appraisals/status-list/",
  // Add this to your endpoints object
  profitData: (from, to) =>
    from && to
      ? `${apiConstants.api_hostname}appraisals/profit-loss/?from=${from}&to=${to}`
      : `${apiConstants.api_hostname}appraisals/profit-loss/`,
  getReceivedRequests: (dealershipId) =>
    `${apiConstants.api_hostname}friend-requests/received/?dealership=${dealershipId}`,
  respondToRequest: (requestId) =>
    `${apiConstants.api_hostname}friend-requests/${requestId}/respond/`,
  dealerCreateProfile: apiConstants.api_hostname + "dealer-profile/",
};

export { axiosInstance, endpoints };
