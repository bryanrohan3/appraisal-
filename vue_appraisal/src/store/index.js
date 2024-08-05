import { createStore } from "vuex";
import createPersistedState from "vuex-persistedstate";

export default createStore({
  state: {
    authToken: null,
    userProfile: null,
    userRole: null, // Add this line
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
      state.userRole = role; // Make sure this line is present
    },
    logout(state) {
      state.authToken = null;
      state.userProfile = null;
      state.userRole = null; // Clear the role on logout
    },
  },

  actions: {},
  plugins: [createPersistedState()],
});
