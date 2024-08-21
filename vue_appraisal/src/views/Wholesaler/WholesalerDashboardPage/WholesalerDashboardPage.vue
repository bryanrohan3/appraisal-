<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Wholesaler Dashboard</h1>
    </div>

    <div class="columns-container">
      <div class="column column-60">
        <!-- Content for the 60% width column goes here -->
        <div class="greetings-container">
          <p class="hello-greetings">
            Hello, {{ userName }} 👋
            <span class="date-now">{{ currentDate }}</span>
          </p>
        </div>
        <p class="time-now">{{ timeOfDay }}</p>
        <!-- Display dealership info -->
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <p class="name">{{ userName }}</p>
          <p class="email">{{ userEmail }}</p>
          <button class="edit-profile-button" @click="goToProfile">
            Edit Profile
          </button>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals"></div>

      <div class="stats-container">
        <div class="stats other-stats"></div>
      </div>
    </div>

    <p>Welcome, {{ userName }}!</p>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";

export default {
  name: "WholesalerDashboardPage",
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
    userEmail() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.email : "";
    },
    timeOfDay() {
      const date = new Date();
      const hours = date.getHours();
      if (hours < 12) {
        return "Good Morning";
      } else if (hours < 18) {
        return "Good Afternoon";
      } else {
        return "Good Evening";
      }
    },
    currentDate() {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date().toLocaleDateString(undefined, options);
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
.dashboard-container {
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px; /* Adjust the max-width as needed */
  padding: 20px;

  box-sizing: border-box; /* Ensure padding and borders are included in the element's total width and height */
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
}

.car-icon {
  width: 20px;
  height: 20px;
}

button {
  padding: 8px 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #ffffff;
  border: 1px solid #000000;
  width: 60%;
  color: #000000;
  cursor: pointer;
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
}

.columns-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.column {
  padding: 10px;
  box-sizing: border-box;
  height: 140px;
  border-radius: 10px;
  /* shadow */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 75%;
  background-color: #ffffff;
}

.column-40 {
  width: 25%; /* Adjust the width as needed */
  background-color: #ffffff;
}

.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center the profile picture and name */
  justify-content: center;
  text-align: center; /* Center the text */
  padding: 10px;
  margin: 0;
  font-size: 16px; /* Adjust the font size as needed */
  font-weight: 400; /* Adjust the font weight as needed */
}

.profile-picture {
  height: 70px; /* Increase the size as needed */
  width: 70px; /* Increase the size as needed */
  border-radius: 50%;
  background-color: #e7e7e7;
  margin-bottom: 10px; /* Space between the picture and the name */
}

.name {
  margin: 0;
}
.email {
  color: #7d7b7b;
  font-size: 12px;
}

/* welcome message styling */
.hello-greetings {
  padding-left: 10px;
  font-size: 15px;
  font-weight: 400;
  margin-bottom: 5px;
}

.hello-greetings {
  padding-left: 40px;
  font-size: 15px;
  font-weight: 400;
  margin-top: 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 10px;
}

.time-now {
  padding-left: 40px;
  margin: 0;
  font-size: 34px;
  font-weight: 500;
  /* space between text letters */
}

/* second container */
.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 50%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  height: 410px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.stats-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.other-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center; /* Center horizontally */
  justify-content: center; /* Center vertically */
  text-align: center; /* Center text */
  gap: 10px;
}
</style>
