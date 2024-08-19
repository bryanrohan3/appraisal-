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
        <div class="greetings-container">
          <p class="hello-greetings">
            Hello, {{ userName }} 👋
            <span class="date-now">{{ currentDate }}</span>
          </p>
        </div>
        <p class="time-now">{{ timeOfDay }}</p>
        <!-- Display dealership info -->
        <div class="dashboard-metrics">
          <div class="metric">
            <div class="circle total-appraisals">
              <img
                src="@/assets/appraisal.svg"
                alt="appraisal"
                class="icon-dash"
              />
            </div>
            <div class="metric-details">
              <span class="metric-value">29</span>
              <span class="metric-title">Total Appraisals</span>
              <!-- <span class="metric-value">{{ totalAppraisals }}</span> -->
            </div>
          </div>
          <div class="metric">
            <div class="circle pending-completions">
              <img src="@/assets/pending.svg" alt="pending" class="icon-dash" />
            </div>
            <div class="metric-details">
              <span class="metric-value">0</span>
              <span class="metric-title">Ongoing Appraisals</span>
              <!-- <span class="metric-value">{{ pendingCompletions }}</span> -->
            </div>
          </div>
          <div class="metric">
            <div class="circle number-of-dealers">
              <img src="@/assets/person.svg" alt="person" class="icon-dash" />
            </div>
            <div class="metric-details">
              <span class="metric-value">7</span>
              <span class="metric-title">Dealership Dealers</span>
              <!-- <span class="metric-value">{{ numberOfDealers }}</span> -->
            </div>
          </div>
        </div>
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <div class="profile-picture"></div>
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
          <p class="stats-name">{{ topWholesalerName }}</p>
        </div>
        <div class="stats other-stats">
          <img class="money" src="@/assets/money.svg" alt="money" />
          <p class="stats-title">Profit/Loss Comparison</p>
          <p class="stats-name">+$100,005</p>
        </div>
        <div class="stats other-stats">
          <img class="car" src="@/assets/car.svg" alt="car" />
          <p class="stats-title">Most Common Car</p>
          <p class="stats-name">{{ mostCommonCarMakeModel }}</p>
        </div>
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
  name: "DealerDashboardPage",
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
    topWholesalerName() {
      return this.topWholesaler &&
        this.topWholesaler.winner__user__wholesaler_name
        ? this.topWholesaler.winner__user__wholesaler_name
        : "Not Available";
    },
    mostCommonCarMakeModel() {
      return this.topCar
        ? `${this.topCar.vehicle_make} ${this.topCar.vehicle_model}`
        : "Not Available";
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
  data() {
    return {
      appraisals: [], // Initialize as an empty array
      topWholesaler: null, // Initialize as null
      topCar: null,
    };
  },
  mounted() {
    this.fetchAppraisals(); // Fetch appraisals data when the component is mounted
    this.fetchTopWholesaler(); // Fetch top wholesaler data when the component is mounted
    this.fetchTopCar();
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
        const response = await axiosInstance.get(
          endpoints.dashboard_appraisals
        );
        this.appraisals = response.data; // Update appraisals data with API response
      } catch (error) {
        console.error("Error fetching appraisals:", error);
      }
    },
    async fetchTopWholesaler() {
      try {
        const response = await axiosInstance.get(endpoints.top_wholesaler);
        this.topWholesaler = response.data.top_wholesaler; // Update top wholesaler data with API response
      } catch (error) {
        console.error("Error fetching top wholesaler:", error);
      }
    },
    async fetchTopCar() {
      try {
        const response = await axiosInstance.get(endpoints.top_car);
        console.log("Top Car Data:", response.data); // Log the data to verify
        this.topCar = response.data; // Ensure this assignment is correct
      } catch (error) {
        console.error("Error fetching top car:", error);
      }
    },
    goToProfile() {
      this.$router.push("/profile");
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
  border: 2px solid white;
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
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
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

/* welcome message styling */
.hello-greetings {
  padding-left: 10px;
  font-size: 15px;
  font-weight: 400;
  margin-bottom: 5px;
}

.hello-greetings {
  padding-left: 10px;
  font-size: 15px;
  font-weight: 400;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 10px;
}

.time-now {
  padding-left: 10px;
  margin: 0;
  font-size: 34px;
  font-weight: 500;
  /* space between text letters */
}

/* dashboard styling */
.dashboard-metrics {
  display: flex; /* Use flexbox for horizontal alignment */
  justify-content: space-between; /* Distribute space evenly */
  gap: 20px; /* Add space between each metric */
  margin-top: 30px;
  padding-left: 10px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1; /* Ensure metrics take up equal space */
}

.circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  position: relative;
  margin-right: 5px;
}

.total-appraisals {
  background-color: #e7e7e7; /* Green */
}

.pending-completions {
  background-color: #e7e7e7; /* Yellow */
}

.number-of-dealers {
  background-color: #e7e7e7; /* Red */
}

.metric-details {
  display: flex;
  flex-direction: column;
}

.metric-title {
  font-size: 14px;
  margin-top: 5px;
  color: #6c757d; /* Light gray */
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
}

/* Add more styles as needed */
.total-appraisals-container {
  font-size: 20px;
  margin-bottom: 20px;
}

.date-filter-container {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.date-filter-container label {
  font-size: 16px;
  font-weight: 500;
}

.date-filter-container input {
  padding: 5px;
  font-size: 16px;
}
</style>
