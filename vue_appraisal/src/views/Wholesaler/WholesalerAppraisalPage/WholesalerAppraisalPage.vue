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

    <div v-if="appraisal" class="appraisals-container">
      <div class="appraisals"></div>

      <div class="stats-container">
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
                placeholder="Reserve Price"
                class="reserve-input"
              />
              <div class="reserve-button">Make Offer</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else>
      <p>Loading appraisal details...</p>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "WholesalerAppraisalPage",
  data() {
    return {
      appraisal: null,
    };
  },
  computed: {
    formattedRegistration() {
      const reg = this.appraisal?.vehicle_registration || "";
      if (reg.length === 6) {
        return `${reg.slice(0, 3)}·${reg.slice(3)}`;
      } else if (reg.length === 7) {
        return `${reg.slice(0, 3)}·${reg.slice(3, 5)} ${reg.slice(5)}`;
      }
      return reg; // Return unformatted if it does not meet the conditions
    },
    formattedVehicleDetails() {
      if (this.appraisal) {
        const year = this.appraisal.vehicle_year || "";
        const make = this.appraisal.vehicle_make || "";
        const model = this.appraisal.vehicle_model || "";
        return `${year} ${make} ${model}`;
      }
      return ""; // Return an empty string or some placeholder text if appraisal is null
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
  background-color: #2e2e2e;
  padding: 20px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
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
  top: 20%;
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
</style>
