<template>
  <div>
    <h1>Dealer Dashboard</h1>
    <p>Welcome, {{ userName }}!</p>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";

export default {
  name: "DealerDashboardPage",
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
  },
  methods: {
    ...mapMutations(["logout"]),
    handleLogout() {
      this.logout(); // Clear Vuex state
      this.$router.push({ name: "login" }); // Redirect to login page
    },
  },
};
</script>

<style scoped>
/* Add your styles here */
</style>
