<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Analytics Overview</h1>
    </div>

    <div class="columns-container">
      <div class="column column-60">
        <div class="dashboard-metrics">
          <div class="metric">
            <div class="stats other-stats">
              <img class="star" src="@/assets/star.svg" alt="Star" />
              <p class="stats-title">Best Performing Wholesaler</p>
              <p class="stats-name">{{ topWholesalerName }}</p>
            </div>
          </div>
          <div class="metric">
            <div class="stats other-stats">
              <img class="money" src="@/assets/money.svg" alt="Money" />
              <p class="stats-title">Profit/Loss Comparison</p>
              <p
                class="stats-name"
                :class="{
                  'positive-profit': totalProfitOrLoss >= 0,
                  'negative-profit': totalProfitOrLoss < 0,
                }"
              >
                {{ totalProfitOrLoss >= 0 ? "+" : ""
                }}{{ totalProfitOrLoss.toLocaleString() }}
              </p>
            </div>
          </div>
          <div class="metric">
            <div class="stats other-stats">
              <img class="car" src="@/assets/car.svg" alt="Car" />
              <p class="stats-title">Most Common Car</p>
              <p class="stats-name">{{ mostCommonCarMakeModel }}</p>
            </div>
          </div>
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
              class="tab-button"
              :class="{ active: currentTab === 'status' }"
              @click="currentTab = 'status'"
            >
              Status
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'mostCommonCars' }"
              @click="currentTab = 'mostCommonCars'"
            >
              Most Common Cars
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'topWholesalers' }"
              @click="currentTab = 'topWholesalers'"
            >
              Top Wholesalers
            </button>
            <button
              class="tab-button"
              :class="{ active: currentTab === 'profit' }"
              @click="currentTab = 'profit'"
            >
              Profit
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

            <div
              v-if="currentTab === 'mostCommonCars'"
              class="most-common-cars-tab"
            >
              <table class="table table-dealer">
                <thead>
                  <tr class="table-header">
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

            <div v-if="currentTab === 'topWholesalers'">
              <table class="table table-dealer">
                <thead>
                  <tr class="table-header">
                    <th>Wholesaler Name</th>
                    <th>Username</th>
                    <th>Count</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(wholesaler, index) in paginatedBestWholesalers"
                    :key="index"
                  >
                    <td>{{ wholesaler.winner__user__wholesaler_name }}</td>
                    <td>{{ wholesaler.winner__user__user__username }}</td>
                    <td>{{ wholesaler.count }}</td>
                  </tr>
                </tbody>
                <p v-if="bestWholesalers.length === 0">
                  No wholesalers found for the selected date range.
                </p>
              </table>
              <p v-if="!bestWholesalers || bestWholesalers.length === 0">
                No wholesalers found for the selected date range.
              </p>

              <!-- Pagination Controls -->
              <div class="pagination-controls">
                <button
                  :disabled="currentPageWholesaler === 1"
                  @click="changePage(currentPageWholesaler - 1)"
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
                  :class="{ active: page === currentPageWholesaler }"
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
                  @click="changePage(currentPageWholesaler + 1)"
                >
                  Next
                </button>
              </div>
            </div>
            <div v-if="currentTab === 'profit'" class="profit-tab">
              <canvas id="profitChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import {
  Chart,
  LineElement,
  LineController,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";

// Register components
Chart.register(
  LineElement,
  LineController,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip
);

export default {
  name: "AnalyticsPage",
  data() {
    return {
      startDate: "",
      endDate: "",
      allCount: 0,
      filteredCount: 0,
      mostCommonCars: [], // Ensure this is initialized as an empty array
      bestWholesalers: [],
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
      currentPageWholesaler: 1, // Add default value for currentPageWholesaler
      pageRange: 2, // Add default value for pageRange
      totalPages: 1, // Ensure totalPages is defined and initialized
      currentTab: "status", // Default tab
      profitData: [], // To store profit data
      profitLabels: [], // To store months or dates for X-axis
      totalProfitOrLoss: 0,
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
    paginatedBestWholesalers() {
      return this.bestWholesalers;
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
    async fetchProfitData() {
      try {
        const params = {};
        if (this.startDate) params.from = this.startDate;
        if (this.endDate) params.to = this.endDate;

        const response = await axiosInstance.get(endpoints.profitData(), {
          params,
        });
        console.log(response.data);

        const data = response.data;

        // Set total profit or loss
        this.totalProfitOrLoss = data.total_profit_or_loss;

        // Process the daily profit data
        this.profitLabels = data.daily_profit.map((item) => item.date);
        this.profitData = data.daily_profit.map((item) => item.profit_or_loss);

        // Render the chart
        this.renderChart();
      } catch (error) {
        console.error("Error fetching profit data:", error);
      }
    },

    generateMonthLabels() {
      const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
      ];
      return months; // Adjust based on actual data range
    },

    renderChart() {
      const ctx = document.getElementById("profitChart").getContext("2d");

      new Chart(ctx, {
        type: "line",
        data: {
          labels: this.profitLabels,
          datasets: [
            {
              label: "Daily Profit",
              data: this.profitData,
              borderColor: "rgba(75, 192, 192, 1)",
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `Profit: ${context.raw}`;
                },
              },
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Date",
              },
              ticks: {
                autoSkip: true,
                maxTicksLimit: 10,
              },
            },
            y: {
              title: {
                display: true,
                text: "Profit/Loss",
              },
              beginAtZero: true,
            },
          },
        },
      });
    },

    // Call fetchProfitData when the tab is switched or on component mount
    fetchData() {
      if (this.currentTab === "profit") {
        this.fetchProfitData();
      }
    },
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
    async fetchBestWholesalers(page = 1) {
      try {
        const params = {
          from: this.startDate || "", // Use the startDate directly if the backend expects YYYY-MM-DD
          to: this.endDate || "", // Use the endDate directly if the backend expects YYYY-MM-DD
          page,
          page_size: this.pageSize,
        };

        console.log("Fetching Most Common Cars with params:", params);
        const response = await axiosInstance.get(
          endpoints.bestWholesalersByDateRange(),
          { params }
        );

        this.bestWholesalers = response.data.results;
        this.totalPages = Math.ceil(response.data.count / this.pageSize);
        this.currentPage = page;
      } catch (error) {
        console.error("Error fetching most common cars:", error);
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
      this.fetchProfitData();
      this.fetchBestWholesalers();
    },
  },
  mounted() {
    this.fetchAllCount();
    this.fetchStatusCounts();
    this.fetchData(); // Fetch data when component mounts
    this.fetchMostCommonCars();
    this.fetchTopWholesaler();
    this.fetchBestWholesalers();
    this.fetchTopCar();
    this.fetchProfitData();
  },
  watch: {
    currentTab(newValue) {
      this.fetchData();
    },
    startDate() {
      this.fetchData();
    },
    endDate() {
      this.fetchData();
    },
  },
};
</script>

<style scoped>
@import "@/assets/utils/table.scss";

/* Pie Chart */
.pie-chart-container {
  display: flex;
  margin: 20px;
  justify-content: center;
  align-items: center;
  margin-left: 60px;
  margin-top: 50px;
  gap: 100px;
}

.pie-chart {
  position: relative;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  overflow: hidden;
}

.pie-chart-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  clip: rect(0, 300px, 300px, 150px);
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
  height: 160px;
  border-radius: 10px;
  /* shadow */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 100%;
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
  width: 100%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  height: 640px; /* Adjust the height as needed for the box with piechart (will need to make bigger)*/
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.stats-container {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  font-size: 13px;
  font-weight: 600;
  color: #7d7b7b; /* Lighter color for the title */
  margin: 0;
}

.stats-name {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.positive-profit {
  color: green;
}

.negative-profit {
  color: red;
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
  gap: 30px;
  margin-top: 60px; /* Added space between pie chart and filtered appraisals */
  justify-content: center; /* Center the filtered appraisals */
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

.status-tab {
  margin-top: 55px;
}
</style>
