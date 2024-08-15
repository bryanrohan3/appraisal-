<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Analytics Overview</h1>
      <div class="notification-button">
        <img src="@/assets/bell.svg" alt="Notification Icon" class="car-icon" />
      </div>
    </div>
    <div class="columns-container">
      <div class="column column-60">
        <!-- Display dealership info -->
        <div class="dashboard-metrics">
          <div class="metric">
            <div class="circle total-appraisals">
              <img
                src="@/assets/appraisal.svg"
                alt="Appraisal"
                class="icon-dash"
              />
            </div>
            <div class="metric-details">
              <span class="metric-value">{{ allCount }}</span>
              <span class="metric-title">Total Appraisals</span>
            </div>
          </div>
          <div class="metric">
            <div class="circle pending-completions">
              <img src="@/assets/pending.svg" alt="Pending" class="icon-dash" />
            </div>
            <div class="metric-details">
              <span class="metric-value">0</span>
              <span class="metric-title">Ongoing Appraisals</span>
            </div>
          </div>
          <div class="metric">
            <div class="circle number-of-dealers">
              <img src="@/assets/person.svg" alt="Dealers" class="icon-dash" />
            </div>
            <div class="metric-details">
              <span class="metric-value">7</span>
              <span class="metric-title">Dealership Dealers</span>
            </div>
          </div>
        </div>
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <div class="profile-picture"></div>
          <p class="name">{{ userName }}</p>
          <p class="email">{{ userEmail }}</p>
          <button class="edit-profile-button">Edit Profile</button>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <div class="filters-container">
          <div class="date-range-filter">
            <div class="date-filter-group">
              <label for="start-date" class="date-label">Start Date</label>
              <input
                type="date"
                id="start-date"
                v-model="startDate"
                class="date-input"
              />
            </div>

            <div class="date-filter-group">
              <label for="end-date" class="date-label">End Date</label>
              <input
                type="date"
                id="end-date"
                v-model="endDate"
                class="date-input"
              />
            </div>

            <button @click="applyDateFilter" class="search-button">
              Apply
            </button>
          </div>
        </div>

        <div class="tabs-container">
          <div class="tabs">
            <button
              :class="{ active: currentTab === 'status' }"
              @click="currentTab = 'status'"
            >
              Status
            </button>
            <button
              :class="{ active: currentTab === 'mostCommonCars' }"
              @click="currentTab = 'mostCommonCars'"
            >
              Most Common Cars
            </button>
          </div>

          <div class="tab-content">
            <div v-if="currentTab === 'status'" class="status-tab">
              <div class="pie-chart-container">
                <div class="pie-chart">
                  <div
                    v-for="(segment, index) in getPieChartSegments()"
                    :key="index"
                    class="pie-chart-segment"
                    :style="segment.style"
                  ></div>
                </div>

                <div class="pie-chart-legend">
                  <p class="legend-title">Status</p>
                  <div
                    v-for="(item, index) in statusCounts"
                    :key="'legend-' + index"
                    class="legend-item"
                  >
                    <div
                      :style="{
                        backgroundColor: getColorForStatus(item.status),
                      }"
                      class="legend-color"
                    ></div>
                    <span class="legend-label">
                      {{ item.status }}: {{ item.count }}
                    </span>
                  </div>
                </div>

                <div class="metric-status">
                  <div class="circle total-appraisals">
                    <img
                      src="@/assets/appraisal.svg"
                      alt="Appraisal"
                      class="icon-dash"
                    />
                  </div>
                  <div class="metric-details">
                    <span class="metric-value">{{ filteredCount }}</span>
                    <span class="metric-title">Filtered Appraisals</span>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-if="currentTab === 'mostCommonCars'"
              class="most-common-cars-tab"
            >
              <table class="cars-table">
                <thead>
                  <tr class="cars-table-header">
                    <th>Make</th>
                    <th>Model</th>
                    <th>Count</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="(car, index) in paginatedMostCommonCars"
                    :key="index"
                  >
                    <td>{{ car.vehicle_make }}</td>
                    <td>{{ car.vehicle_model }}</td>
                    <td>{{ car.count }}</td>
                  </tr>
                </tbody>
                <p v-if="mostCommonCars.length === 0">
                  No cars found for the selected date range.
                </p>
              </table>
              <p v-if="!mostCommonCars || mostCommonCars.length === 0">
                No cars found for the selected date range.
              </p>

              <!-- Pagination Controls -->
              <div class="pagination-controls">
                <button
                  :disabled="currentPage === 1"
                  @click="changePage(currentPage - 1)"
                >
                  Previous
                </button>
                <button v-if="showFirstPageButton" @click="changePage(1)">
                  1
                </button>
                <button v-if="showEllipsisLeft" disabled>...</button>
                <button
                  v-for="page in visiblePageNumbers"
                  :key="page"
                  :class="{ active: page === currentPage }"
                  @click="changePage(page)"
                >
                  {{ page }}
                </button>
                <button v-if="showEllipsisRight" disabled>...</button>
                <button
                  v-if="showLastPageButton"
                  @click="changePage(totalPages)"
                >
                  {{ totalPages }}
                </button>
                <button
                  :disabled="currentPage === totalPages"
                  @click="changePage(currentPage + 1)"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-container">
        <div class="stats other-stats">
          <img class="star" src="@/assets/star.svg" alt="Star" />
          <p class="stats-title">Best Performing Wholesaler</p>
          <p class="stats-name">{{ topWholesalerName }}</p>
        </div>
        <div class="stats other-stats">
          <img class="money" src="@/assets/money.svg" alt="Money" />
          <p class="stats-title">Profit/Loss Comparison</p>
          <p class="stats-name">+$100,005</p>
        </div>
        <div class="stats other-stats">
          <img class="car" src="@/assets/car.svg" alt="Car" />
          <p class="stats-title">Most Common Car</p>
          <p class="stats-name">{{ mostCommonCarMakeModel }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "AnalyticsPage",
  data() {
    return {
      startDate: "",
      endDate: "",
      allCount: 0,
      filteredCount: 0,
      mostCommonCars: [], // Ensure this is initialized as an empty array
      topWholesaler: null,
      topCar: null,
      statusCounts: [], // Ensure this is initialized as an empty array
      allStatuses: [
        "Pending - Sales",
        "Pending - Management",
        "Complete",
        "Active",
        "Trashed",
      ],
      pageSize: 10, // Add default value for pageSize
      currentPage: 1, // Add default value for currentPage
      pageRange: 2, // Add default value for pageRange
      totalPages: 1, // Ensure totalPages is defined and initialized
      currentTab: "status", // Default tab
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
    paginatedMostCommonCars() {
      return this.mostCommonCars;
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
  methods: {
    async fetchAllCount() {
      try {
        const response = await axiosInstance.get(endpoints.allCount);
        this.allCount = response.data.count;
      } catch (error) {
        console.error("Error fetching all count:", error);
      }
    },
    async fetchFilteredCount() {
      try {
        const params = {};
        if (this.startDate) params.start_date = this.startDate;
        if (this.endDate) params.end_date = this.endDate;

        const response = await axiosInstance.get(endpoints.allCount, {
          params,
        });
        this.filteredCount = response.data.count;
      } catch (error) {
        console.error("Error fetching filtered count:", error);
      }
    },
    async fetchStatusCounts() {
      try {
        const params = {};
        if (this.startDate) params.from = `${this.startDate}T00:00:00Z`;
        if (this.endDate) params.to = `${this.endDate}T23:59:59Z`;

        const response = await axiosInstance.get(endpoints.statusList, {
          params,
        });

        // Ensure all statuses are represented
        const data = response.data;
        this.statusCounts = this.allStatuses.map((status) => {
          const found = data.find((item) => item.status === status);
          return { status, count: found ? found.count : 0 };
        });
      } catch (error) {
        console.error("Error fetching status counts:", error);
      }
    },
    async fetchMostCommonCars(page = 1) {
      try {
        const params = {
          from: this.startDate || "", // Use the startDate directly if the backend expects YYYY-MM-DD
          to: this.endDate || "", // Use the endDate directly if the backend expects YYYY-MM-DD
          page,
          page_size: this.pageSize,
        };

        console.log("Fetching Most Common Cars with params:", params);
        const response = await axiosInstance.get(
          endpoints.mostCommonCarsByDateRange(),
          { params }
        );

        this.mostCommonCars = response.data.results;
        this.totalPages = Math.ceil(response.data.count / this.pageSize);
        this.currentPage = page;
      } catch (error) {
        console.error("Error fetching most common cars:", error);
      }
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.fetchMostCommonCars(page);
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
    getPieChartSegments() {
      // Calculate the total number of counts across all status segments.
      const total = this.statusCounts.reduce(
        (acc, item) => acc + item.count,
        0
      );

      // Initialize the starting angle for the first segment.
      let startAngle = 0;

      // Iterate through each status count and calculate the style for each segment.
      return this.statusCounts.map((item) => {
        // Calculate the percentage of the pie that this segment represents.
        const percentage = total > 0 ? (item.count / total) * 100 : 0;

        // Determine the end angle for this segment of the pie chart.
        const endAngle = startAngle + (360 * percentage) / 100;

        // Create the style object for this segment.
        const style = {
          transform: `rotate(${startAngle}deg)`, // Rotate the segment to start at the correct angle.
          background: `conic-gradient(${this.getColorForStatus(
            item.status
          )} ${percentage}%, transparent ${percentage}%)`, // Create a gradient for the segment with the appropriate color and transparency.
        };

        // Update the starting angle for the next segment to start where this one ends.
        startAngle = endAngle;

        // Return an object containing the status and style for this segment.
        return {
          status: item.status,
          style,
        };
      });
    },

    getColorForStatus(status) {
      switch (status) {
        case "Complete":
          return "#eb5a58"; // Green
        case "Pending - Sales":
          return "#ff8f06"; // Orange
        case "Pending - Management":
          return "#3059d3"; // Blue
        case "Active":
          return "#65bd70"; // Yellow
        case "Trashed":
          return "#9e9e9e"; // Gray
        default:
          return "#b2b2b2"; // Light gray
      }
    },

    applyDateFilter() {
      this.fetchFilteredCount();
      this.fetchStatusCounts();
      this.fetchMostCommonCars();
      this.fetchTopWholesaler();
      this.fetchTopCar();
    },
  },
  mounted() {
    this.fetchAllCount();
    this.fetchStatusCounts();
    this.fetchMostCommonCars();
    this.fetchTopWholesaler();
    this.fetchTopCar();
  },
};
</script>

<style scoped>
.tabs-container {
  margin-bottom: 20px;
}

.tabs {
  display: flex;
  margin-left: 20px;
}

.tabs button {
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

.tabs button.active {
  border-bottom: 2px solid #eb5a58;
  color: #333;
  font-weight: 600;
}

.tab-content {
  padding: 20px;
  padding-top: 0px;
}

/* Pie Chart */
.pie-chart-container {
  display: flex;
  margin: 20px;
  margin-left: 40px;
}

.pie-chart {
  position: relative;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
}

.pie-chart-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  clip: rect(0, 200px, 200px, 100px);
  border-radius: 50%;
  transform-origin: center;
  transition: transform 1s ease-in-out, background 1s ease-in-out; /* Added transition */
}

.pie-chart-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  color: #000;
  text-align: center;
}

.pie-chart-legend {
  margin-left: 20px;
  display: flex;
  flex-direction: column;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 10px;
}

.legend-label {
  font-size: 14px;
  font-weight: 500;
}

.legend-title {
  font-size: 16px;
  margin-bottom: 10px;
}

/* Dashboard Container */
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

/*button {
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
}*/

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
  height: 410px; /* Adjust the height as needed for the box with piechart (will need to make bigger)*/
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

.metric-status {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1; /* Ensure metrics take up equal space */
  margin-left: 60px;
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

/* Date Filter */
.filters-container {
  display: flex;
  padding-left: 0;
}

.date-range-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff;
  padding: 8px;
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

/* card styling */
.most-common-cars-container {
  margin: 20px;
}

/* Cars Table Styling */
.cars-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
}

.cars-table th,
.cars-table td {
  text-align: left;
  padding: 6px 10px;
  font-size: 12px;
}

.cars-table tr {
  margin: 0;
}

.cars-table th {
  font-weight: 400;
  padding-bottom: 5px;
}

.cars-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.cars-table tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

.cars-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 12px;
  color: #7d7b7b;
}

/* Pagination Controls */
.pagination-controls {
  margin-top: 40px;
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
</style>
