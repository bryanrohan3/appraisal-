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
    <!-- <div class="columns-container">
      <div class="column column-60">
        <p class="">hey</p>
      </div>
    </div> -->

    <transition
      name="fade"
      @before-enter="beforeEnter"
      @enter="enter"
      @leave="leave"
    >
      <div class="appraisals-container">
        <div class="appraisals">
          <div class="tabs">
            <button
              class="tab-button"
              :class="{ active: currentTab === 'all' }"
              @click="
                currentTab = 'all';
                fetchAppraisals();
              "
            >
              All Appraisals
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'pending - sales' }"
              @click="
                currentTab = 'pending - sales';
                fetchAppraisals();
              "
            >
              Pending - Sales
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'pending - management' }"
              @click="
                currentTab = 'pending - management';
                fetchAppraisals();
              "
            >
              Pending - Management
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'active' }"
              @click="
                currentTab = 'active';
                fetchAppraisals();
              "
            >
              Active
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'complete' }"
              @click="
                currentTab = 'complete';
                fetchAppraisals();
              "
            >
              Complete
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'trashed' }"
              @click="
                currentTab = 'trashed';
                fetchAppraisals();
              "
            >
              Trashed
            </button>
          </div>
          <!-- Search Bar -->
          <!-- Search Bar and Action Buttons -->
          <div class="search-bar-container">
            <div class="search-bar">
              <input
                type="text"
                v-model="searchQuery"
                placeholder="Search for appraisals ID, car make, car model, VIN, etc..."
                @input="debouncedSearch"
              />
            </div>
            <div class="action-buttons">
              <button @click="exportData" class="export-button">
                <img
                  src="@/assets/download.svg"
                  alt="Download Icon"
                  class="button-icon"
                />
                Export CSV
              </button>
              <button @click="openFilter" class="filter-button">
                <img
                  src="@/assets/filter.svg"
                  alt="Car Icon"
                  class="button-icon"
                />
                Filter
              </button>
            </div>
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
              <tr v-for="appraisal in appraisals" :key="appraisal.id">
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
        </div>
        <div class="pagination-controls">
          <button
            :disabled="currentPage === 1"
            @click="fetchAppraisals(currentPage - 1)"
          >
            Previous
          </button>
          <button v-if="showFirstPageButton" @click="fetchAppraisals(1)">
            1
          </button>
          <button v-if="showEllipsisLeft" disabled>...</button>
          <button
            v-for="page in visiblePageNumbers"
            :key="page"
            :class="{ active: page === currentPage }"
            @click="fetchAppraisals(page)"
          >
            {{ page }}
          </button>
          <button v-if="showEllipsisRight" disabled>...</button>
          <button
            v-if="showLastPageButton"
            @click="fetchAppraisals(totalPages)"
          >
            {{ totalPages }}
          </button>
          <button
            :disabled="currentPage === totalPages"
            @click="fetchAppraisals(currentPage + 1)"
          >
            Next
          </button>
        </div>
        <span class="total-records"
          >Total Appraisals: {{ totalAppraisals }}</span
        >
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
      appraisals: [],
      searchQuery: "",
      currentTab: "all",
      currentPage: 1,
      totalPages: 1,
      pageSize: 10,
      totalAppraisals: 0,
      pageRange: 2,
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
    pageNumbers() {
      const pages = [];
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
      return pages;
    },
    visiblePageNumbers() {
      const start = Math.max(1, this.currentPage - this.pageRange);
      const end = Math.min(this.totalPages, this.currentPage + this.pageRange);

      const adjustedStart = Math.max(1, end - this.pageRange * 2);

      return this.pageNumbers.filter(
        (page) => page >= adjustedStart && page <= end
      );
    },
    showFirstPageButton() {
      return this.totalPages > 1 && this.visiblePageNumbers[0] > 1;
    },
    showLastPageButton() {
      return (
        this.totalPages > 1 &&
        this.visiblePageNumbers[this.visiblePageNumbers.length - 1] <
          this.totalPages
      );
    },
    showEllipsisLeft() {
      return this.showFirstPageButton && this.visiblePageNumbers[0] > 2;
    },
    showEllipsisRight() {
      return (
        this.showLastPageButton &&
        this.visiblePageNumbers[this.visiblePageNumbers.length - 1] <
          this.totalPages - 1
      );
    },
  },
  mounted() {
    this.fetchAppraisals();
    this.debouncedSearch = debounce(this.search, 1000);
  },
  methods: {
    ...mapMutations(["logout"]),
    handleLogout() {
      this.logout();
      this.$router.push({ name: "login" });
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
      el.offsetHeight;
      el.style.transition = "opacity 0.3s ease";
      el.style.opacity = 1;
      done();
    },
    leave(el, done) {
      el.style.transition = "opacity 0.3s ease";
      el.style.opacity = 0;
      done();
    },
    fetchAppraisals(page = 1) {
      const filter = this.searchQuery ? `&filter=${this.searchQuery}` : "";
      const status =
        this.currentTab !== "all" ? `&status=${this.currentTab}` : "";

      console.log(
        `Fetching appraisals with page=${page}, filter=${filter}, status=${status}`
      );

      axiosInstance
        .get(`${endpoints.appraisals}/?page=${page}${filter}${status}`)
        .then((response) => {
          console.log("Response data:", response.data); // Log API response
          this.appraisals = response.data.results;
          this.totalAppraisals = response.data.count;
          this.totalPages = Math.ceil(this.totalAppraisals / this.pageSize);
          this.currentPage = page;
        })
        .catch((error) => {
          console.error("Error fetching appraisals:", error);
        });
    },
    exportData() {
      const filter = this.searchQuery ? `?filter=${this.searchQuery}` : "";
      axiosInstance
        .post(`${endpoints.appraisals}/${filter}`, null, {
          responseType: "blob", // Set the response type to 'blob' to handle the CSV file
        })
        .then((response) => {
          // Create a URL for the blob object
          const url = window.URL.createObjectURL(new Blob([response.data]));
          // Create an anchor element and set its href to the URL
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "appraisals.csv"); // Set the file name for download
          document.body.appendChild(link);
          link.click(); // Programmatically click the link to trigger the download
        })
        .catch((error) => {
          console.error("Error exporting data:", error);
        });
    },
    search() {
      this.fetchAppraisals(1);
    },
  },
  watch: {
    searchQuery: "debouncedSearch",
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
  color: #333333;
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
  /*margin: 20px 0;*/
  gap: 20px;
}

.appraisals {
  width: 100%;
  background-color: #ffffff;
  padding: 20px;
  box-sizing: border-box;
  height: 560px;
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
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  outline: none;
}

/* Search Bar and Action Buttons */
.search-bar-container {
  display: flex;
  justify-content: space-between;
}

.search-bar {
  flex: 1;
}

.action-buttons {
  display: flex;
}

.export-button,
.filter-button {
  display: flex;
  padding: 8px 16px;
  margin-left: 10px;
  font-size: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  height: 32.5px;
}

.export-button:hover,
.filter-button:hover {
  background-color: #e0e0e0;
}

.button-icon {
  width: 16px; /* Adjust size as needed */
  height: 16px; /* Adjust size as needed */
  margin-right: 8px; /* Space between icon and text */
  vertical-align: middle;
}

.export-button:hover,
.filter-button:hover {
  background-color: #e0e0e0;
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
  width: 00px; /* Adjust width as needed */
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
  font-size: 11px;
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
  position: relative;
  padding-left: 0;
  padding-right: 0;
  justify-content: flex-start; /* Align tabs to the left */
}

.tab-button {
  background-color: transparent;
  border: none;
  padding: 10px 20px; /* Adjust padding as needed */
  margin-right: 10px; /* Add space between buttons */
  cursor: pointer;
  font-size: 12px;
  text-align: center;
  color: #b0b0b0;
  position: relative;
}

.tab-button.active {
  color: #333;
  font-weight: 600;
}

.tab-button::after {
  content: "";
  display: block;
  height: 2px;
  background-color: #eb5a58;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: scaleX(0);
  transform-origin: bottom left;
  transition: transform 0.3s ease;
}

.tab-button.active::after {
  transform: scaleX(1);
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
  background-color: #f26764;
  color: #fff;
}

.pagination-controls button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.total-records {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #999;
}
</style>
