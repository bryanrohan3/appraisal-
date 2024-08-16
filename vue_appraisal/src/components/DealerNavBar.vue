<template>
  <div class="navbar-wrapper">
    <div class="navbar">
      <div class="logo-container">
        <img src="@/assets/logo.svg" class="logo" />
        <p class="company">i@ppraisal</p>
      </div>
      <router-link
        to="/dashboard"
        :class="{ 'active-link': isActive('/dashboard') }"
      >
        <div class="nav-item">
          <img
            :src="
              isActive('/')
                ? require('@/assets/dashboard-active.svg')
                : require('@/assets/dashboard.svg')
            "
            class="icon"
          />
          <a>Dashboard</a>
        </div>
      </router-link>

      <router-link
        to="/appraisals"
        :class="{ 'active-link': isActive('/appraisals') }"
      >
        <div class="nav-item">
          <img
            :src="
              isActive('/appraisals')
                ? require('@/assets/appraisal-icon-active.svg')
                : require('@/assets/appraisal-icon.svg')
            "
            class="icon"
          />
          <a>Appraisals</a>
        </div>
      </router-link>

      <router-link
        to="/create-appraisal"
        :class="{ 'active-link': isActive('/create-appraisal') }"
      >
        <div class="nav-item">
          <img
            :src="
              isActive('/create-appraisal')
                ? require('@/assets/create-appraisal-active.svg')
                : require('@/assets/create-appraisal.svg')
            "
            class="icon"
          />
          <a>Create</a>
        </div>
      </router-link>

      <router-link
        to="/analytics"
        :class="{ 'active-link': isActive('/analytics') }"
      >
        <div class="nav-item">
          <!-- <img src="@/assets/analytics.svg" class="icon" /> -->
          <img
            :src="
              isActive('/analytics')
                ? require('@/assets/analytics-active.svg')
                : require('@/assets/analytics.svg')
            "
            class="icon"
          />
          <a>Analytics</a>
        </div>
      </router-link>

      <router-link
        to="/requests"
        :class="{ 'active-link': isActive('/requests') }"
      >
        <div class="nav-item">
          <img src="@/assets/requests.svg" class="icon" />
          Requests
        </div>
      </router-link>

      <div class="logout-container">
        <button @click="handleLogout" class="logout-button">
          <img src="@/assets/logout.svg" class="logout-icon" />
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapMutations } from "vuex";

export default {
  name: "DealerNavBar",
  methods: {
    ...mapMutations(["logout"]),
    handleLogout() {
      this.logout(); // Clear Vuex state
      this.$router.push({ name: "login" }); // Redirect to login page
    },
    isActive(route) {
      return this.$route.path.startsWith(route);
    },
  },
};
</script>

<style scoped>
@font-face {
  font-family: "LogoFont"; /* Choose a name for your font */
  src: url("@/assets/fonts/AirbnbCereal_W_Blk.otf") format("opentype");
  font-weight: normal;
  font-style: normal;
}

html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #ffffff;
}

.icon {
  margin-right: 10px;
}

.logo-container {
  display: flex;
  align-items: center;
  padding-left: 10px;
  margin-top: 20px;
}

.logo {
  width: 30px; /* Adjust size as needed */
  height: auto;
  margin-right: 10px;
}

.company {
  font-weight: 800;
  font-size: 24px;
  color: #f26764;
  font-weight: 600;
  font-family: "LogoFont";
}

.navbar-wrapper {
  height: 100vh; /* Full viewport height */
  position: fixed; /* Fix the navbar */
  display: flex;
}

.navbar {
  width: 200px; /* Adjust width as needed */
  height: 100vh; /* Full viewport height */
  background-color: #ffffff; /* Example background color */
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Space between nav items and logout button */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.nav-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
  color: #333;
}

.nav-item:hover {
  background-color: #f1f1f1;
}

.nav-item svg {
  margin-right: 10px;
}

.navbar a {
  text-decoration: none;
  color: #aaa;
  font-weight: 500;
  font-size: 14px;
}

.nav-item .icon {
  transition: transform 0.3s ease;
}

.nav-item:hover .icon {
  transform: scale(1.1);
}

.logout-container {
  margin-top: auto; /* Pushes the logout button to the bottom */
  padding: 10px;
}

.logout-button {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  margin-top: auto; /* Ensure it stays at the bottom */
  border-radius: 5px;
  color: #f26764;
  background: #ffffff;
  border: 3px solid #ffffff;
  border-radius: 10px;
  margin-bottom: 50px;
  width: 100%;
  font-weight: 800;
  font-size: 16px;
}

.logout-button:hover {
  background-color: #f1f1f1;
}

.logout-icon {
  margin-right: 10px;
}

.active-link .nav-item a {
  color: #f26764; /* Red color for the active link */
  font-weight: 600;
}

/* Ensure this is applied to active nav items */
.navbar .router-link-exact-active .nav-item a {
  color: #f26764;
  font-weight: 600;
}
</style>
