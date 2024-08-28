<template>
  <div class="content-container">
    <div class="title-container">
      <p class="title">
        <router-link
          :to="{ name: 'WholesalerAppraisalsPage' }"
          class="appraisals-link"
        >
          Appraisals</router-link
        >
        <span class="separator">/</span> {{ formattedVehicleDetails }}
      </p>
    </div>

    <div class="tabs">
      <!-- Appraisal tab (always shown) -->
      <button
        class="tab-button"
        :class="{ active: currentTab === 'appraisal' }"
        @click="currentTab = 'appraisal'"
      >
        Appraisal
      </button>

      <!-- Offers and Comments tabs (only shown if viewing an appraisal) -->

      <button
        class="tab-button"
        :class="{ active: currentTab === 'comments' }"
        @click="currentTab = 'comments'"
      >
        Comments
      </button>
    </div>

    <div
      v-if="currentTab === 'appraisal' && appraisal"
      class="appraisals-container"
    >
      <div class="appraisals">
        <div class="photos-section">
          <div class="photo-placeholder">
            <p>No photos available</p>
          </div>
        </div>

        <div class="description-section">
          <p class="description">
            {{ appraisal.vehicle_year }} {{ appraisal.vehicle_make }}
            {{ appraisal.vehicle_model }}
          </p>
        </div>

        <div>
          <p class="odometer">{{ appraisal.odometer_reading }} mi.</p>
        </div>

        <div class="vehicle-details-section">
          <h2 class="headers-more">Basics</h2>
          <table class="details-table">
            <tr>
              <th>Year</th>
              <td>{{ appraisal.vehicle_year }}</td>
            </tr>
            <tr>
              <th>Make</th>
              <td>{{ appraisal.vehicle_make }}</td>
            </tr>
            <tr>
              <th>Model</th>
              <td>{{ appraisal.vehicle_model }}</td>
            </tr>
            <tr>
              <th>Engine Type</th>
              <td>{{ appraisal.engine_type }}</td>
            </tr>
            <tr>
              <th>Odometer Reading</th>
              <td>{{ appraisal.odometer_reading }} mi</td>
            </tr>
          </table>
        </div>

        <div class="vehicle-details-section">
          <h2 class="headers-more">More Details</h2>
          <table class="details-table">
            <tr>
              <th>VIN</th>
              <td>{{ appraisal.vehicle_vin }}</td>
            </tr>
            <tr>
              <th>Vehicle Registration</th>
              <td>{{ appraisal.vehicle_registration }}</td>
            </tr>
            <tr>
              <th>Colour</th>
              <td>{{ appraisal.color }}</td>
            </tr>
            <tr>
              <th>Body Type</th>
              <td>{{ appraisal.body_type }}</td>
            </tr>
            <tr>
              <th>Transmission</th>
              <td>{{ appraisal.transmission }}</td>
            </tr>
            <tr>
              <th>Fuel Type</th>
              <td>{{ appraisal.fuel_type }}</td>
            </tr>
          </table>
        </div>

        <div class="vehicle-details-section">
          <h2 class="headers-more">Sellers Info</h2>
          <table class="details-table">
            <tr>
              <th>Dealership</th>
              <td>{{ appraisal.dealership.dealership_name }}</td>
            </tr>
            <tr>
              <th>Initiating Dealer</th>
              <td>
                {{ appraisal.initiating_dealer.first_name }}
                {{ appraisal.initiating_dealer.last_name }}
              </td>
            </tr>
            <tr>
              <th>Last Updating Dealer</th>
              <td>
                {{ appraisal.last_updating_dealer.first_name }}
                {{ appraisal.last_updating_dealer.last_name }}
              </td>
            </tr>
          </table>
        </div>
      </div>

      <div class="stats-container">
        <div class="status-container">
          <div :class="getStatusClass(appraisal.status)">
            {{ appraisal.status }}
          </div>
        </div>

        <div v-if="appraisal" class="number-plate">
          <div class="registration">{{ formattedRegistration }}</div>
          <div class="dealership">AUSTRALIA - APPRAISAL</div>
        </div>
        <div class="stats other-stats">
          <p class="small-header">Make Offer</p>
          <div class="reserve-price-container">
            <div class="reserve-input-wrapper">
              <span class="reserve-icon">$</span>
              <input
                type="number"
                placeholder="Make Offer"
                class="reserve-input"
                v-model="offerAmount"
              />
              <div class="reserve-button" @click="makeOffer">Make Offer</div>
              <p class="or">or</p>
              <div class="reserve-button" @click="passOnOffer">Pass</div>
            </div>
          </div>
        </div>
        <table class="details-table">
          <tr v-for="offer in appraisal.offers" :key="offer.id">
            <th>Amount</th>
            <td>
              <!-- Display logic based on the conditions -->
              <span v-if="offer.amount === null && !offer.passed"
                >No offer made</span
              >
              <span v-else-if="offer.amount !== null && !offer.passed">{{
                offer.amount
              }}</span>
              <span v-else-if="offer.passed && offer.amount === null"
                >Passed</span
              >
              <span v-else>N/A</span>
            </td>
          </tr>
        </table>
      </div>
    </div>

    <div v-if="currentTab === 'comments'">
      <CommentTab :appraisal="appraisal" />
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import CommentTab from "@/components/CommentTab.vue";

export default {
  name: "WholesalerAppraisalPage",
  data() {
    return {
      appraisal: null,
      currentTab: "appraisal",
      offerAmount: null, // To store the offer amount
      offer: {
        amount: null,
        passed: false,
      },
    };
  },
  components: {
    CommentTab,
  },
  computed: {
    formattedRegistration() {
      const reg = this.appraisal?.vehicle_registration || "";
      if (reg.length === 6) {
        return `${reg.slice(0, 3)}·${reg.slice(3)}`;
      } else if (reg.length === 7) {
        return `${reg.slice(0, 3)}·${reg.slice(3, 5)} ${reg.slice(5)}`;
      }
      return reg;
    },
    formattedVehicleDetails() {
      if (this.appraisal) {
        const year = this.appraisal.vehicle_year || "";
        const make = this.appraisal.vehicle_make || "";
        const model = this.appraisal.vehicle_model || "";
        return `${year} ${make} ${model}`;
      }
      return "";
    },
  },
  created() {
    this.fetchAppraisal();
  },
  methods: {
    fetchAppraisal() {
      const id = this.$route.params.id;
      axiosInstance
        .get(`${endpoints.all_appraisals}${id}/`)
        .then((response) => {
          this.appraisal = response.data;
        })
        .catch((error) => {
          console.error("Error fetching appraisal details:", error);
        });
    },
    makeOffer() {
      const appraisalId = this.$route.params.id;
      if (this.offerAmount) {
        axiosInstance
          .post(endpoints.makeOffer(appraisalId), { amount: this.offerAmount })
          .then(() => {
            alert("Offer made successfully!");
            this.offerAmount = null; // Clear the input after a successful offer
          })
          .catch((error) => {
            console.error("Error making offer:", error);
            alert("Failed to make an offer.");
          });
      } else {
        alert("Please enter an offer amount.");
      }
    },
    passOnOffer() {
      const appraisalId = this.$route.params.id;
      axiosInstance
        .post(endpoints.passOnOffer(appraisalId))
        .then(() => {
          alert("You have passed on this offer.");
          this.offerAmount = null; // Clear the input when passing
        })
        .catch((error) => {
          console.error("Error passing on offer:", error);
          alert("Failed to pass on the offer.");
        });
    },
    getStatusClass(status) {
      switch (status) {
        case "Active":
          return "status-active";
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
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fira+Code:wght@300..700&display=swap");

.number-plate {
  display: flex;
  flex-direction: column; /* Stack the registration and dealership vertically */
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    145deg,
    #e0e0e0,
    #f1f1f1
  ); /* Gradient background for a more realistic look */
  color: #660000; /* Maroon color similar to the number plate */
  border: 2px solid #660000; /* Maroon border */
  border-radius: 8px;
  font-family: "Fira Code", monospace;
  font-weight: bold;

  text-align: center;
  max-width: 220px; /* Adjust width as needed */
  padding: 10px 20px;

  box-shadow: inset 5px 5px 10px rgba(0, 0, 0, 0.3);
}

.registration {
  font-size: 36px; /* Larger text for the registration number */
  letter-spacing: 4px; /* Spacing between characters */
  text-shadow: 3px 1px 2px rgba(0, 0, 0, 0.3); /* Adds depth to the text */
}

.dealership {
  font-size: 9px; /* Smaller text for the dealership name */
  letter-spacing: 2px; /* Spacing between characters */
  margin-top: 1px; /* Slight margin to separate from the registration */
  text-shadow: 3px 1px 1px rgba(0, 0, 0, 0.2); /* Adds subtle depth to the text */
}

.content-container {
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px;
  padding: 20px;

  box-sizing: border-box;
}

.title-container {
  margin-top: 10px;
  display: flex;
  align-items: center;
}

.appraisals-link {
  text-decoration: underline;
  color: #ccc; /* Adjust color as needed */
  cursor: pointer;
  margin-right: 8px; /* Adds spacing between the link and the separator */
}

.appraisals-link:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 8px; /* Adds spacing around the separator */
  color: #f26764; /* Color of the separator */
}

.title {
  font-size: 14px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  color: #ccc;
}
/* Table Styling */
.appraisals-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px auto;
  background-color: #2e2e2e;
  border-radius: 5px;
}

.appraisals-table th,
.appraisals-table td {
  text-align: left;
  padding: 6px 10px;
  font-size: 12px;
  color: #e0e0e0;
}

.appraisals-table th {
  font-weight: 400;
  padding-bottom: 5px;
}

.appraisals-table tr:nth-child(even) {
  background-color: #3c3c3c; /* Slightly lighter dark background for even rows */
}
.appraisals-table tr:hover {
  background-color: #4c4c4c; /* Highlight color for rows on hover */
  cursor: pointer;
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  color: #c0c0c0; /* Light color for dark mode */
}

/* new code */
.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px; /* Space between the containers */
}

.appraisals {
  box-sizing: border-box;
  border-radius: 10px;
  flex: 3; /* Takes more space relative to .stats-container */
  height: 400px;
  min-height: 200px; /* Ensure it has a minimum height */
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 20px; /* Space between the stats items */
  flex: 1; /* Takes less space relative to .appraisals */
}

.number-plate {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    145deg,
    #e0e0e0,
    #f1f1f1
  ); /* Gradient background for a more realistic look */
  color: #660000; /* Maroon color similar to the number plate */
  border: 2px solid #660000; /* Maroon border */
  border-radius: 8px;
  font-family: "Fira Code", monospace;
  font-weight: bold;
  text-align: center;
  max-width: 220px; /* Adjust width as needed */
  padding: 10px 20px;
  box-shadow: inset 5px 5px 10px rgba(0, 0, 0, 0.3);
}

.registration {
  font-size: 36px; /* Larger text for the registration number */
  letter-spacing: 4px; /* Spacing between characters */
  text-shadow: 3px 1px 2px rgba(0, 0, 0, 0.3); /* Adds depth to the text */
}

.dealership {
  font-size: 9px; /* Smaller text for the dealership name */
  letter-spacing: 2px; /* Spacing between characters */
  margin-top: 1px; /* Slight margin to separate from the registration */
  text-shadow: 3px 1px 1px rgba(0, 0, 0, 0.2); /* Adds subtle depth to the text */
}

.stats {
  background-color: #2e2e2e;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  min-height: 100px; /* Ensure it has a minimum height */
}

/* Make an Offer */
.reserve-price-container {
  display: flex;
  align-items: center;
  width: 100%; /* Ensure the container takes full width */
}

.reserve-input-wrapper {
  position: relative;
  width: 90%; /* Ensure the wrapper takes full width */
}

.reserve-icon {
  position: absolute;
  top: 11%;
  transform: translateY(-50%);
  pointer-events: none; /* Prevents the icon from blocking input interaction */
  color: #ccc; /* Adjust the color as needed */
  font-size: 18px; /* Adjust the size as needed */
  font-weight: 400;
}

.reserve-input {
  width: 100%;
  padding-left: 30px; /* Add padding to make space for the icon */
  padding: 10px;
  border: 2px solid #1f1f1f;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  height: 39px;
  margin-left: 20px;
  background-color: #1f1f1f;
  margin-bottom: 10px;
  color: #ccc;
}

.small-header {
  font-size: 12px;
  color: #ccc;
  padding-left: 20px;
  margin-top: 10px;
  font-weight: 500;
}

.reserve-button {
  background-color: #f26764; /* Button background color */
  border: none; /* Remove default border */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 5px;
  font-size: 12px;
  color: #ffffff;
  width: 100%;

  margin-bottom: 10px;
}

/* Mock Photos Section */
.photos-section {
  background-color: #3c3c3c;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.photo-placeholder {
  background-color: #555;
  height: 350px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ddd;
  font-size: 14px;
}

/* Details Table */
.details-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  table-layout: fixed;
}

.details-table th,
.details-table td {
  padding: 10px;
  text-align: left;
}

.details-table th {
  border-bottom: #555 1px solid;
  color: #ccc;
  font-size: 14px;
}

.details-table td {
  color: #ddd;
  border-bottom: #555 1px solid;
  font-weight: 200;
}

.headers {
  font-size: 28px;
  margin-bottom: 5px;
  font-size: 14px;
}

.headers-more {
  font-size: 28px;
  margin-bottom: 5px;
  margin-top: 50px;
}

.description {
  font-size: 24px;
  line-height: 1.5;
  margin-bottom: 10px;
  font-weight: 300;
}

.odometer {
  font-size: 18px;
  margin-bottom: 10px;
  margin-top: 0px;
  font-weight: 300;
  color: #ccc;
}

.status {
  font-size: 13px;
  margin-top: 0px;
  font-weight: 300;
  color: #ccc;
  font-weight: 600;
  padding: 10px;
  background-color: #2e2e2e;
  border-radius: 25px;
  text-align: center;
}

/* Specific color classes for status */
.status-pending-sales {
  background-color: #efd4b3; /* Orange for Pending - Sales */
  color: #ff8f06;
  font-weight: 600;

  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
}

.status-pending-management {
  background-color: #9dc6f0; /* Dodger Blue for Pending - Management */
  color: #3059d3;
  font-weight: 600;

  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
}

.status-active {
  background-color: #e0f2e5; /* Green for Active */
  color: #65bd70;
  font-weight: 600;

  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
}

.status-complete {
  background-color: #f6c6c6; /* Red for Complete */
  color: #eb5a58;
  font-weight: 600;

  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
}

.status-trashed {
  background-color: #b2b2b2; /* Grey for Trashed */
  color: #fff;
  font-weight: 600;

  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
}

.or {
  font-size: 13px;
  margin-top: 0px;
  font-weight: 600;
  padding: 10px;
  border-radius: 25px;
  text-align: center;
  padding: 0%;
  color: #ccc;
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
  color: #f26764;
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
</style>
