// store/index.js
import { createStore } from "vuex";
import createPersistedState from "vuex-persistedstate";

export default createStore({
  state: {
    authToken: null,
    userProfile: null,
    userRole: null,
  },
  getters: {
    getAuthToken(state) {
      return state.authToken;
    },
    getUserProfile(state) {
      return state.userProfile;
    },
    getUserRole(state) {
      return state.userRole;
    },
  },
  mutations: {
    setAuthToken(state, token) {
      state.authToken = token;
    },
    setUserProfile(state, user) {
      state.userProfile = user;
    },
    setUserRole(state, role) {
      state.userRole = role;
    },
    logout(state) {
      state.authToken = null;
      state.userProfile = null;
      state.userRole = null;
    },
  },
  actions: {
    fetchUserProfile({ commit }) {
      axiosInstance
        .get(endpoints.dealerProfile)
        .then((response) => {
          const profile = response.data;
          commit("setUserProfile", profile);
          commit("setUserRole", profile.role);
        })
        .catch((error) => {
          console.error("Error fetching user profile:", error);
        });
    },
  },
  plugins: [createPersistedState()],
});
