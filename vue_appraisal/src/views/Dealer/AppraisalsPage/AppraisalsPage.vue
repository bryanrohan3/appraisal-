<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Appraisals Overview</h1>
      <div class="info-icon">
        <span class="info-icon-circle">?</span>
        <div class="tooltip">
          This page provides an overview of all appraisals. Here you can search
          for specific appraisals by ID, car make, car model, VIN, and see all
          Appraisals associated with the current user.
        </div>
      </div>
    </div>
    <div class="columns-container">
      <div class="column column-60">
        <div class="tabs">
          <button
            class="tab-button"
            :class="{ active: currentTab === 'all' }"
            @click="currentTab = 'all'"
          >
            All Appraisals
          </button>
          <button
            class="tab-button"
            :class="{ active: currentTab === 'pending - sales' }"
            @click="currentTab = 'pending - sales'"
          >
            Pending - Sales
          </button>
          <button
            class="tab-button"
            :class="{ active: currentTab === 'pending - management' }"
            @click="currentTab = 'pending - management'"
          >
            Pending - Management
          </button>
          <button
            class="tab-button"
            :class="{ active: currentTab === 'active' }"
            @click="currentTab = 'active'"
          >
            Active
          </button>
          <button
            class="tab-button"
            :class="{ active: currentTab === 'complete' }"
            @click="currentTab = 'complete'"
          >
            Complete
          </button>
          <button
            class="tab-button"
            :class="{ active: currentTab === 'trashed' }"
            @click="currentTab = 'trashed'"
          >
            Trashed
          </button>
        </div>
      </div>
    </div>

    <transition
      name="fade"
      @before-enter="beforeEnter"
      @enter="enter"
      @leave="leave"
    >
      <div class="appraisals-container">
        <div class="appraisals">
          <!-- Search Bar -->
          <div class="search-bar">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search for appraisals ID, car make, car model, VIN, etc..."
              @input="debouncedSearch"
            />
          </div>
          <!-- Table -->
          <table class="appraisals-table">
            <thead>
              <tr class="appraisals-table-header">
                <th>ID</th>
                <th>Client Name</th>
                <th>Car Make</th>
                <th>Car Model</th>
                <th>VIN</th>
                <th>Rego</th>
                <th>Status</th>
                <th>Initiating Dealer</th>
              </tr>
            </thead>
            <tbody>
              <!-- Filtered rows based on searchQuery -->
              <tr v-for="appraisal in filteredAppraisals" :key="appraisal.id">
                <td>{{ appraisal.id }}</td>
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
                <td>
                  {{ appraisal.initiating_dealer.first_name }}
                  {{ appraisal.initiating_dealer.last_name }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
        </div>
        <div class="pagination-controls">
          <button
            :disabled="currentPage === 1"
            @click="fetchAppraisals(currentPage - 1)"
          >
            Previous
          </button>
          <button
            v-for="page in pageNumbers"
            :key="page"
            :class="{ active: page === currentPage }"
            @click="fetchAppraisals(page)"
          >
            {{ page }}
          </button>
          <button
            :disabled="currentPage === totalPages"
            @click="fetchAppraisals(currentPage + 1)"
          >
            Next
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import debounce from "lodash/debounce";

export default {
  name: "DealerDashboardPage",
  data() {
    return {
      appraisals: [], // Initialize as an empty array
      searchQuery: "", // Data property for search input
      currentTab: "all",
      currentPage: 1,
      totalPages: 1,
      pageSize: 10,
      totalAppraisals: 0,
    };
  },
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
    filteredAppraisals() {
      const search = this.searchQuery.toLowerCase();
      const currentTabStatus = this.currentTab.toLowerCase().trim();

      return this.appraisals.filter((appraisal) => {
        const fullName =
          `${appraisal.customer_first_name} ${appraisal.customer_last_name}`.toLowerCase();
        const appraisalStatus = appraisal.status
          ? appraisal.status.toLowerCase().trim()
          : "";

        const statusMatch =
          this.currentTab === "all" || appraisalStatus === currentTabStatus;

        return (
          statusMatch &&
          (fullName.includes(search) ||
            appraisal.vehicle_make.toLowerCase().includes(search) ||
            appraisal.vehicle_model.toLowerCase().includes(search) ||
            appraisal.vehicle_vin.toLowerCase().includes(search) ||
            appraisal.vehicle_registration.toLowerCase().includes(search) ||
            appraisalStatus.includes(search))
        );
      });
    },
    pageNumbers() {
      const pages = [];
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
      return pages;
    },
  },
  mounted() {
    this.fetchAppraisals(); // Fetch appraisals data when the component is mounted
    this.debouncedSearch = debounce(this.search, 300);
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
    beforeEnter(el) {
      el.style.opacity = 0;
    },
    enter(el, done) {
      el.offsetHeight; // Trigger reflow
      el.style.transition = "opacity 0.3s ease";
      el.style.opacity = 1;
      done();
    },
    leave(el, done) {
      el.style.transition = "opacity 0.3s ease";
      el.style.opacity = 0;
      done();
    },
    async fetchAppraisals(page = 1) {
      try {
        const response = await axiosInstance.get(
          `${endpoints.all_appraisals}?page=${page}`
        );
        this.appraisals = response.data.results; // Update appraisals data with API response
        this.totalAppraisals = response.data.count;
        this.pageSize = response.data.results.length; // Adjust if page size changes dynamically
        this.totalPages = Math.ceil(this.totalAppraisals / this.pageSize);
        this.currentPage = page;
      } catch (error) {
        console.error("Error fetching appraisals:", error);
      }
    },
    search() {
      this.filteredAppraisals; // Trigger computed property update
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
  height: 110px;
  border-radius: 10px;
  /* shadow */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 100%;
  background-color: #ffffff;
}

/* Appraisal List */
.appraisals-listings {
  width: 75%;
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
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 100%;
  background-color: #ffffff;
  padding: 20px;
  box-sizing: border-box;
  height: 490px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.search-bar {
  margin-bottom: 10px;
  color: #65bd70;
}

.search-bar input {
  width: 100%;
  padding: 8px;
  font-size: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  outline: none;
}

/* Tooltip */
.info-icon {
  display: inline-block;
  position: relative;
  margin-left: 5px; /* Reduce the left margin to bring it closer */
}

.info-icon-circle {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: #a2a2a2; /* Circle color */
  color: white;
  text-align: center;
  line-height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
}

.tooltip {
  visibility: hidden;
  width: 200px; /* Adjust width as needed */
  background-color: #333; /* Tooltip background color */
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 5px 10px;
  position: absolute;
  z-index: 1;
  bottom: 125%; /* Position above the icon */
  left: 50%;
  margin-left: -100px; /* Center the tooltip */
  opacity: 0;
  font-size: 10px;
  transition: opacity 0.3s;
}

.info-icon:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.info-icon {
  display: inline-block;
  position: relative;
  margin-left: 5px; /* Adjust this value to move the icon closer */
}

.tooltip {
  visibility: hidden;
  width: 300px; /* Adjust width as needed */
  background-color: #333; /* Tooltip background color */
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 5px 10px;
  position: absolute;
  z-index: 1;
  bottom: 125%; /* Position above the icon */
  left: 105%; /* Adjust this value to position the tooltip closer to the icon */
  margin-left: 0; /* Remove the centering margin */
  opacity: 0;
  transition: opacity 0.3s;
}

/* Tabs */
.tabs {
  display: flex;
  margin-bottom: 20px;
  position: relative; /* Positioning context for the slider */
  padding-left: 0; /* Remove or reduce padding if necessary */
  padding-right: 0; /* Remove or reduce padding if necessary */
}

.tab-button {
  background-color: transparent; /* Transparent background */
  border: none; /* Remove default border */
  padding: 10px 0 10px 0;
  margin-right: 2px; /* Reduce space between buttons */
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  text-align: center;
  position: relative; /* Positioning context for the bottom border */
  color: #b0b0b0; /* Light gray color for inactive tabs */
  cursor: pointer;
}

.tab-button.active {
  color: #333; /* Dark color for the active tab */
  font-weight: 600;
}

/* Slider/Indicator under active tab */
.tab-button::after {
  content: "";
  display: block;
  height: 2px; /* Slider height */
  background-color: #eb5a58; /* Slider color */
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: scaleX(0); /* Start with zero width */
  transform-origin: bottom left;
  transition: transform 0.3s ease; /* Smooth transition */
}

.tab-button.active::after {
  transform: scaleX(1); /* Expand to full width */
}

.tab-button {
  background-color: transparent; /* Transparent background */
  border: none; /* Remove default border */
  padding: 10px 0;
  margin-right: 5px; /* Reduced space between buttons */
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  text-align: center;
  position: relative; /* Positioning context for the bottom border */
  color: #b0b0b0; /* Light gray color for inactive tabs */
}

.tab-button.active {
  color: #333; /* Dark color for the active tab */
  font-weight: 600;
}

/* Pagination Controls */
.pagination-controls {
  margin-top: 20px;
  text-align: center;
}

.pagination-controls button {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  color: #333;
  cursor: pointer;
  margin: 0 5px;
  padding: 5px 10px;
}

.pagination-controls button.active {
  background-color: #007bff;
  color: #fff;
}

.pagination-controls button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
