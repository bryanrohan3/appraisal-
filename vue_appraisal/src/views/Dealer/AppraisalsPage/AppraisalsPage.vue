<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 :class="titleClass">Appraisals Overview</h1>
      <div class="info-icon">
        <span class="info-icon-circle">?</span>
        <div class="tooltip">
          This page provides an overview of all appraisals. Here you can search
          for specific appraisals by ID, car make, car model, VIN, and see all
          Appraisals associated with the current user.
        </div>
      </div>
    </div>

    <div :class="filtersContainerClass">
      <!-- Date Range Filter -->
      <div :class="dateRangeFilterClass">
        <div :class="dateFilterGroupClass">
          <label for="start-date" :class="dateLabelClass">Start Date</label>
          <input
            type="date"
            id="start-date"
            v-model="startDate"
            :class="dateInputClass"
          />
        </div>

        <div :class="dateFilterGroupClass">
          <label for="end-date" :class="dateLabelClass">End Date</label>
          <input
            type="date"
            id="end-date"
            v-model="endDate"
            :class="dateInputClass"
          />
        </div>

        <button @click="applyDateFilter" class="search-button">Apply</button>
      </div>
    </div>

    <transition
      name="fade"
      @before-enter="beforeEnter"
      @enter="enter"
      @leave="leave"
    >
      <div class="appraisals-container">
        <div :class="appraisalsClass">
          <div class="tabs" v-if="this.userRole === 'dealer'">
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
              :class="{ active: currentTab === 'Pending - Sales' }"
              @click="
                currentTab = 'Pending - Sales';
                fetchAppraisals();
              "
            >
              Pending - Sales
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Pending - Management' }"
              @click="
                currentTab = 'Pending - Management';
                fetchAppraisals();
              "
            >
              Pending - Management
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Active' }"
              @click="
                currentTab = 'Active';
                fetchAppraisals();
              "
            >
              Active
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Complete' }"
              @click="
                currentTab = 'Complete';
                fetchAppraisals();
              "
            >
              Complete
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Trashed' }"
              @click="
                currentTab = 'Trashed';
                fetchAppraisals();
              "
            >
              Trashed
            </button>
          </div>

          <div class="tabs" v-if="this.userRole === 'wholesaler'">
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
              :class="{ active: currentTab === 'Complete - Priced' }"
              @click="
                currentTab = 'Complete - Priced';
                fetchAppraisals();
              "
            >
              Complete - Priced
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Complete - Won' }"
              @click="
                currentTab = 'Complete - Won';
                fetchAppraisals();
              "
            >
              Complete - Won
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Active' }"
              @click="
                currentTab = 'Active';
                fetchAppraisals();
              "
            >
              Active
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Complete - Lost' }"
              @click="
                currentTab = 'Complete - Lost';
                fetchAppraisals();
              "
            >
              Complete - Lost
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'Complete - Missed' }"
              @click="
                currentTab = 'Complete - Missed';
                fetchAppraisals();
              "
            >
              Complete - Missed
            </button>
          </div>

          <!-- Search Bar -->
          <div class="search-bar-container">
            <div :class="inputClass">
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
                  src="@/assets/filter-list.svg"
                  alt="Car Icon"
                  class="button-icon"
                />
                Filter
              </button>
            </div>
          </div>
          <!-- Table -->
          <table :class="tableClass" v-if="this.userRole === 'dealer'">
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
                <th>Winner</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="appraisal in appraisals"
                :key="appraisal.id"
                @click="viewAppraisal(appraisal.id)"
              >
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
                <td>
                  <!-- display winner and if null display null -->
                  <span v-if="appraisal.winner">
                    {{ appraisal.winner.username }}
                  </span>
                  <span v-else>null</span>
                </td>
              </tr>
            </tbody>
          </table>

          <table :class="tableClass" v-else="this.userRole === 'wholesaler'">
            <thead>
              <tr class="appraisals-table-header">
                <th>ID</th>
                <th>Initiating Dealer</th>
                <th>Dealership</th>
                <th>Car Make</th>
                <th>Car Model</th>
                <th>VIN</th>
                <th>Rego</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="appraisal in appraisals"
                :key="appraisal.id"
                @click="viewAppraisal(appraisal.id)"
              >
                <td>{{ appraisal.id }}</td>
                <td>
                  {{ appraisal.initiating_dealer.first_name }}
                  {{ appraisal.initiating_dealer.last_name }}
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
  name: "AppraisalsPage",
  data() {
    return {
      appraisals: [],
      searchQuery: "",
      currentTab: "all",
      currentPage: 1,
      totalPages: 1,
      pageSize: 10,
      totalAppraisals: 0,
      startDate: null, // New data property for start date
      endDate: null, // New data property for end date
      pageRange: 2, // Define pageRange here
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
    userRole() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.role : "guest"; // Adjust 'role' according to your user profile structure
    },
    titleClass() {
      return this.userRole === "wholesaler"
        ? "title-wholesaler"
        : "title-dealer";
    },
    appraisalsClass() {
      return this.userRole === "wholesaler"
        ? "appraisals-wholesaler"
        : "appraisals-dealer";
    },
    tableClass() {
      return this.userRole === "wholesaler"
        ? "appraisals-table-wholesaler"
        : "appraisals-table-dealer";
    },
    inputClass() {
      return this.userRole === "wholesaler"
        ? "search-bar-wholesaler"
        : "search-bar-dealer";
    },
    filtersContainerClass() {
      return this.userRole === "wholesaler"
        ? "filters-container-dark"
        : "filters-container-light";
    },
    dateRangeFilterClass() {
      return this.userRole === "wholesaler"
        ? "date-range-filter-dark"
        : "date-range-filter-light";
    },
    dateFilterGroupClass() {
      return this.userRole === "wholesaler"
        ? "date-filter-group-dark"
        : "date-filter-group-light";
    },
    dateLabelClass() {
      return this.userRole === "wholesaler"
        ? "date-label-dark"
        : "date-label-light";
    },
    dateInputClass() {
      return this.userRole === "wholesaler"
        ? "date-input-dark"
        : "date-input-light";
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
        case "Complete - Won":
          return "status-pending-management";
        case "Complete - Lost":
          return "status-complete";
        case "Complete - Priced":
          return "status-pending-sales";
        case "Complete - Missed":
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
      console.log("Current Tab:", this.currentTab); // Log current tab value

      const searchQuery = this.searchQuery ? `&filter=${this.searchQuery}` : ""; // Log search query
      const status =
        this.currentTab !== "all" ? `&filter=${this.currentTab}` : ""; // Log status filter
      const start = this.startDate ? `&start_date=${this.startDate}` : ""; // Log start date filter
      const end = this.endDate ? `&end_date=${this.endDate}` : ""; // Log end date filter

      const url = `${endpoints.appraisals}/?page=${page}${searchQuery}${status}${start}${end}`;
      console.log("Final URL:", url);

      axiosInstance
        .get(url)
        .then((response) => {
          this.appraisals = response.data.results;
          this.totalAppraisals = response.data.count;
          this.totalPages = Math.ceil(this.totalAppraisals / this.pageSize);
          this.currentPage = page;
        })
        .catch((error) => {
          console.error("Error fetching appraisals:", error);
        });
    },
    search() {
      this.fetchAppraisals();
    },
    exportData() {
      // Construct the filter parameter based on the current tab and search query
      const filters = [];
      if (this.currentTab !== "all") {
        filters.push(`filter=${this.currentTab}`);
      }
      if (this.searchQuery) {
        filters.push(`filter=${this.searchQuery}`);
      }

      // Create the query string
      const queryString = filters.join("&");
      const url = `${endpoints.appraisals}/?${queryString}`;

      axiosInstance
        .post(url, null, {
          responseType: "blob", // Handle binary data
        })
        .then((response) => {
          // Create a Blob from the response data
          const blob = new Blob([response.data], { type: "text/csv" });
          const downloadUrl = URL.createObjectURL(blob);

          // Create an anchor element and trigger a download
          const link = document.createElement("a");
          link.href = downloadUrl;
          link.download = "appraisals.csv";
          document.body.appendChild(link); // Append the link to the body
          link.click();
          document.body.removeChild(link); // Remove the link after downloading

          // Clean up
          URL.revokeObjectURL(downloadUrl);
        })
        .catch((error) => {
          console.error("Error exporting data:", error);
        });
    },
    openFilter() {
      this.showFilterModal = true;
    },
    applyDateFilter() {
      this.fetchAppraisals(); // Re-fetch appraisals with the new date filters
    },
    changePage(page) {
      this.fetchAppraisals(page);
    },
    viewAppraisal(id) {
      this.$router.push({ name: "AppraisalViewPage", params: { id } });
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

.appraisals-table tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
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
  color: #eb5a58;
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

/* Date Filter */
.filters-container {
  display: flex;
  padding: 10px;
  padding-left: 0;
}

.date-range-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.date-filter-group {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.date-input {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 12px;
  width: 120px;
}

.date-input:focus {
  border-color: #007bff;
  outline: none;
}

.search-button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background-color: #eb5a58;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #a43b39;
}

/* Define styles for wholesalers */
.title-wholesaler {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
  color: #eee;
}

.appraisals-wholesaler {
  width: 100%;
  background-color: #282828;
  padding: 20px;
  box-sizing: border-box;
  height: 560px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

/* Define styles for dealers */
.title-dealer {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
  color: #333333;
}

.appraisals-dealer {
  width: 100%;
  background-color: #ffffff;
  padding: 20px;
  box-sizing: border-box;
  height: 560px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

/* Add other styles as needed */

/* Light Mode (Dealer) */
.appraisals-table-dealer {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
}

.appraisals-table-dealer th,
.appraisals-table-dealer td {
  text-align: left;
  padding: 6px 10px;
  font-size: 12px;
}

.appraisals-table-dealer tr {
  margin: 0;
}

.appraisals-table-dealer th {
  font-weight: 400;
  padding-bottom: 5px;
}

.appraisals-table-dealer tr:nth-child(even) {
  background-color: #f9f9f9;
}

.appraisals-table-dealer tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 12px;
  color: #7d7b7b;
}

/* Dark Mode (Wholesaler) */
.appraisals-table-wholesaler {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
  background-color: #2e2e2e; /* Dark background for the table */
}

.appraisals-table-wholesaler th,
.appraisals-table-wholesaler td {
  text-align: left;
  padding: 6px 10px;
  font-size: 12px;
  color: #e0e0e0; /* Light text color for dark mode */
}

.appraisals-table-wholesaler tr {
  margin: 0;
}

.appraisals-table-wholesaler th {
  font-weight: 400;
  padding-bottom: 5px;
  background-color: #1c1c1c; /* Darker background for headers */
}

.appraisals-table-wholesaler tr:nth-child(even) {
  background-color: #3c3c3c; /* Slightly lighter dark background for even rows */
}

.appraisals-table-wholesaler tr:hover {
  background-color: #4c4c4c; /* Highlight color for rows on hover */
  cursor: pointer;
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 12px;
  color: #c0c0c0; /* Light color for dark mode */
}

/* Search Bar */
.search-bar-dealer input {
  width: 100%;
  padding: 8px;
  font-size: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  outline: none;
}

.search-bar-wholesaler {
  flex: 1;
}

.search-bar-dealer {
  flex: 1;
}

/* Dark Mode (Wholesaler) */
.search-bar-wholesaler input {
  width: 100%;
  padding: 8px;
  font-size: 12px;
  border: 1px solid #444; /* Darker border for dark mode */
  border-radius: 4px;
  box-sizing: border-box;
  outline: none;
  background-color: #282828; /* Dark background for input */
  color: #b0b0b0; /* Light text color for dark mode */
}

/* Date Filter */
/* Light Mode Styles */
.filters-container-light {
  display: flex;
  padding: 10px;
  padding-left: 0;
}

.date-range-filter-light {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.date-filter-group-light {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-label-light {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.date-input-light {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 12px;
  width: 120px;
}

.date-input-light:focus {
  border-color: #007bff;
  outline: none;
}

/* Dark Mode (Wholesaler) */
/* Dark Mode Styles */
.filters-container-dark {
  display: flex;
  padding: 10px;
  padding-left: 0;
}

.date-range-filter-dark {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #2e2e2e;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.date-filter-group-dark {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-label-dark {
  font-size: 12px;
  color: #bbb;
  white-space: nowrap;
}

.date-input-dark {
  padding: 6px;
  border: 1px solid #555;
  border-radius: 4px;
  font-size: 12px;
  width: 120px;
  background-color: #222;
  color: #eee;
}

.date-input-dark:focus {
  border-color: #66b2ff;
  outline: none;
}
</style>
