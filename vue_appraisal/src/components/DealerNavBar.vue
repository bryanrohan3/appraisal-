<template>
  <div class="navbar-wrapper">
    <div class="navbar">
      <div class="logo-container">
        <img src="@/assets/logo.svg" class="logo" />
        <p class="company">i@ppraisal</p>
      </div>
      <router-link to="#">
        <div class="nav-item">
          <img src="@/assets/dashboard.svg" class="icon" />
          <a href="/">Dashboard</a>
        </div>
      </router-link>

      <a class="nav-item">
        <img src="@/assets/search.svg" class="icon" />
        <a>Search</a>
      </a>

      <div class="nav-item">
        <img src="@/assets/appraisal-icon.svg" class="icon" />
        <a>Appraisals</a>
      </div>

      <router-link to="#">
        <div class="nav-item">
          <img src="@/assets/create-appraisal.svg" class="icon" />
          <a>Create</a>
        </div>
      </router-link>

      <router-link to="#">
        <div class="nav-item">
          <img src="@/assets/analytics.svg" class="icon" />
          Analytics
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "DealerNavBar",
};
</script>

<style scoped>
@font-face {
  font-family: "YourCustomFont"; /* Choose a name for your font */
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
  font-family: "YourCustomFont";
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
  justify-content: flex-start; /* Align items to the start of the container */
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
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.nav-item .icon {
  transition: transform 0.3s ease;
}

.nav-item:hover .icon {
  transform: scale(1.1);
}
</style>
