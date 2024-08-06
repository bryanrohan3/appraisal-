<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Dealer Dashboard Overview</h1>
      <div class="notification-button">
        <img src="@/assets/bell.svg" alt="Car Icon" class="car-icon" />
      </div>
    </div>
    <div class="columns-container">
      <div class="column column-60">
        <!-- Content for the 60% width column goes here -->
        <!-- Display dealership info -->
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <div class="profile-picture"></div>
          <p class="name">{{ userName }}</p>
          <p class="email">{{ getUserProfile.email }}</p>
          <button class="edit-profile-button">Edit Profile</button>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <p class="recent-appraisals">Recent Appraisals</p>
        <table class="appraisals-table">
          <thead>
            <tr class="appraisals-table-header">
              <th>Client Name</th>
              <th>Car Make</th>
              <th>Car Model</th>
              <th>VIN</th>
              <th>Rego</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <!-- Example rows; replace with actual data -->
            <tr v-for="appraisal in appraisals" :key="appraisal.id">
              <td>
                {{ appraisal.customer_first_name }}
                {{ appraisal.customer_last_name }}
              </td>
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

      <div class="stats-container">
        <div class="stats other-stats">
          <img class="star" src="@/assets/star.svg" alt="star" />
          <p class="stats-title">Best Performing Wholesaler</p>
          <p class="stats-name">Charlie Cameron</p>
        </div>
        <div class="stats other-stats">
          <img class="money" src="@/assets/money.svg" alt="money" />
          <p class="stats-title">Profit/Loss Comparison</p>
          <p class="stats-name">+$100,005</p>
        </div>
        <div class="stats other-stats">
          <img class="car" src="@/assets/car.svg" alt="car" />
          <p class="stats-title">Most Common Car</p>
          <p class="stats-name">Volkswagen Jetta</p>
        </div>
      </div>
    </div>

    <p>Welcome, {{ userName }}!</p>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { axiosInstance } from "@/helpers/axiosHelper";

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
  data() {
    return {
      appraisals: [], // Initialize as an empty array
    };
  },
  mounted() {
    this.fetchAppraisals(); // Fetch appraisals data when the component is mounted
  },
  methods: {
    ...mapMutations(["logout"]),
    handleLogout() {
      this.logout(); // Clear Vuex state
      this.$router.push({ name: "login" }); // Redirect to login page
    },
    getStatusClass(status) {
      switch (status) {
        case "Pending - Sales":
          return "status-pending-sales";
        case "Pending - Management":
          return "status-pending-management";
        case "Active":
          return "status-active";
        case "Complete":
          return "status-complete";
        case "Trashed":
          return "status-trashed";
        default:
          return "";
      }
    },
    async fetchAppraisals() {
      try {
        const response = await axiosInstance.get("appraisals/simple-list/");
        this.appraisals = response.data; // Update appraisals data with API response
      } catch (error) {
        console.error("Error fetching appraisals:", error);
      }
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px; /* Adjust the max-width as needed */
  padding: 20px;
  padding-left: 200px; /* Optional: Add padding inside the container */
  box-sizing: border-box; /* Ensure padding and borders are included in the element's total width and height */
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.notification-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e4e4e4;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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
  height: 210px;
  border-radius: 10px;
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

/* Appraisal List */
.appraisals-listings {
  width: 75%;
  background-color: #ffffff;
}

.popular-wholesaler {
  width: 25%; /* Adjust the width as needed */
  background-color: #ffffff;
}

.recent-appraisals {
  font-size: 16px;
  font-weight: 400;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  padding-left: 10px;
}

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
  background-color: #f9f9f9;
}

.appraisals-table tr {
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 12px;
  color: #7d7b7b;
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

/* new code */
.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 75%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  height: 410px;
  border-radius: 10px;
}

.stats-container {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
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

.stats-title {
  font-size: 10px;
  font-weight: 600;
  color: #7d7b7b; /* Lighter color for the title */
  margin: 0;
}

.stats-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}
</style>
