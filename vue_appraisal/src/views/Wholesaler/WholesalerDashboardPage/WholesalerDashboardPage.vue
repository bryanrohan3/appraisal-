<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Wholesaler Dashboard</h1>
    </div>

    <div class="columns-container">
      <div class="column column-60">
        <div class="greetings-container">
          <div class="greetings">
            <p class="hello-greetings">Hello, {{ userName }} 👋</p>
            <div class="time-of-day">
              <p class="time-now">{{ timeOfDay }}</p>
            </div>
          </div>

          <div v-if="wholesalerProfileInfo" class="wholesaler-info">
            <p class="company-name">
              {{ wholesalerProfileInfo.wholesaler_name }}
            </p>
            <p class="email">{{ wholesalerProfileInfo.street_address }}</p>
            <p class="email">{{ wholesalerProfileInfo.suburb }}</p>
            <p class="email">{{ wholesalerProfileInfo.postcode }}</p>
            <p class="email">{{ wholesalerProfileInfo.phone }}</p>
          </div>

          <span class="date-now">{{ currentDate }}</span>
        </div>
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
      <div class="appraisals">
        <p class="recent-appraisals">Recent Appraisals</p>
        <table class="appraisals-table">
          <thead>
            <tr class="appraisals-table-header">
              <th>Dealer Name</th>
              <th>Dealership</th>
              <th>Car Make</th>
              <th>Car Model</th>
              <th>VIN</th>
              <th>Rego</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appraisal in appraisals" :key="appraisal.id">
              <td>
                {{ appraisal.last_updating_dealer.first_name }}
                {{ appraisal.last_updating_dealer.last_name }}
              </td>
              <td>{{ appraisal.dealership.dealership_name }}</td>
              <td>{{ appraisal.vehicle_make }}</td>
              <td>{{ appraisal.vehicle_model }}</td>
              <td>{{ appraisal.vehicle_vin }}</td>
              <td>{{ appraisal.vehicle_registration }}</td>
              <td>
                <span
                  :class="getStatusClass(appraisal.status)"
                  class="status-word"
                >
                  {{ appraisal.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p>Welcome, {{ userName }}!</p>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

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
    goToProfile() {
      this.$router.push("/wholesaler/profile");
    },
  },
  data() {
    return {
      appraisals: [],
      wholesalerProfileInfo: null,
    };
  },
  mounted() {
    this.fetchAppraisals();
    this.fetchWholesalerProfileInfo();
  },
  methods: {
    ...mapMutations(["logout"]),
    handleLogout() {
      this.logout(); // Clear Vuex state
      this.$router.push({ name: "login" }); // Redirect to login page
    },
    getStatusClass(status) {
      switch (status) {
        case "Active":
          return "status-pending-sales";
        case "Complete - Lost":
          return "status-pending-management";
        case "Complete - Won":
          return "status-active";
        case "Complete - Priced":
          return "status-complete";
        case "Complete - Missed":
          return "status-trashed";
        default:
          return "";
      }
    },
    async fetchAppraisals() {
      try {
        const response = await axiosInstance.get(
          endpoints.wholesaler_dashboard_appraisals
        );
        this.appraisals = response.data; // Update appraisals data with API response
      } catch (error) {
        console.error("Error fetching appraisals:", error);
      }
    },
    async fetchWholesalerProfileInfo() {
      try {
        const response = await axiosInstance.get(endpoints.wholesalerProfile);
        this.wholesalerProfileInfo = response.data; // Store the wholesaler profile data
        console.log("Wholesaler Profile Response:", response.data);
      } catch (error) {
        console.error("Error fetching wholesaler profile information:", error);
      }
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
  color: #eee;
}

.car-icon {
  width: 20px;
  height: 20px;
}

button {
  margin-top: 10px;
  padding: 8px 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #f26764;
  border: 1px solid #eee;
  width: 60%;
  color: #eee;
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

.column-60 {
  width: 75%;
  background-color: #282828;
}

.column-40 {
  width: 25%; /* Adjust the width as needed */
  background-color: #282828;
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
  margin-left: 20px;
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
  color: #eee;
}
.email {
  color: #aaa;
  font-size: 12px;
}

.time-now {
  padding-left: 40px;
  margin: 0;
  font-size: 34px;
  font-weight: 500;
  color: #eee;
  /* space between text letters */
}

/* second container */
.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 100%;
  background-color: #282828;
  padding: 10px;
  box-sizing: border-box;
  height: 410px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

/* Table Styling */
/* Table Styling */
.appraisals-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
}

.appraisals-table th,
.appraisals-table td {
  text-align: left;
  padding: 6px 10px;
  font-size: 12px;
}

.appraisals-table tr {
  margin: 0;
}

.appraisals-table th {
  font-weight: 400;

  padding-bottom: 5px;
}

.appraisals-table tr:nth-child(even) {
  background-color: #3f3f3f;
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 12px;
  color: #a8a5a5;
}

/* Status color styling */
.status-word {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  text-align: center;
  display: inline-block;
}

/* Specific color classes for status */
.status-pending-sales {
  background-color: #efd4b3; /* Orange for Pending - Sales */
  color: #ff8f06;
  font-weight: 600;
}

.status-pending-management {
  background-color: #9dc6f0; /* Dodger Blue for Pending - Management */
  color: #3059d3;
  font-weight: 600;
}

.status-active {
  background-color: #e0f2e5; /* Green for Active */
  color: #65bd70;
  font-weight: 600;
}

.status-complete {
  background-color: #f6c6c6; /* Red for Complete */
  color: #eb5a58;
  font-weight: 600;
}

.status-trashed {
  background-color: #b2b2b2; /* Grey for Trashed */
  color: #fff;
  font-weight: 600;
}

/* New Code */
.column {
  padding: 10px;
  box-sizing: border-box;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
  background-color: #282828;
  display: flex;
}

.greetings-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* Welcome message styling */
.greetings {
  flex: 1;
}

.hello-greetings {
  padding-left: 40px;
  font-size: 15px;
  font-weight: 400;
  display: flex;
  font-size: 14px;
  font-weight: 400;
  color: #eee;
  margin-bottom: 5px;
  padding-top: 0px;
  margin-top: 0px;
}

.time-of-day-greeting {
  font-size: 14px;
  color: #ccc;
  margin: 0;
}

.date-now {
  font-size: 14px;
  color: #aaa;
  margin-right: 40px;
}

.wholesaler-info {
  flex: 1;
  margin-left: 40px;
  color: #eee;
}

.wholesaler-info p {
  margin: 2px 0;
}

/* Time of day styling */
.time-of-day {
  flex: 1;
}

.time-now {
  font-size: 34px;
  font-weight: 500;
  color: #eee;
}
</style>
